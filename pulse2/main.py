import asyncio
import json
import time
import serial
from collections import deque
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.algorithm import PulseAlgorithm
from models.schemas import PulseReport

# ===== 全局状态管理 =====
measurement_session = {
    "is_measuring": False,
    "hr_history": [],
    "spo2_history": [],
}

# 实例化算法
algo = PulseAlgorithm(buffer_size=100, fs=50)

# WebSocket 连接池
active_connections = set()

# 串口配置
SERIAL_PORT = "COM9"
BAUD_RATE = 115200

# 🔧 关键修复：用滑动窗口累积数据
ir_window = deque(maxlen=100)
red_window = deque(maxlen=100)


async def serial_worker():
    """
    串口后台任务
    🔧 修复点：
    1. 用滑动窗口累积 100 个点
    2. 每次只发送少量波形点（减少传输量，提高频率）
    3. 确保 q 字段正确传递
    """
    print(f"🔄 串口已连接: {SERIAL_PORT}, 算法采样率: 50Hz")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)

        while True:
            if ser.in_waiting:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()

                    if line.startswith('{"ir":'):
                        data = json.loads(line)
                        ir_list = data['ir']
                        red_list = data['red']

                        # === 🔧 修复1：逐个添加到滑动窗口 ===
                        for i in range(len(ir_list)):
                            ir_window.append(ir_list[i])
                            red_window.append(red_list[i])

                        # === 🔧 修复2：窗口满了才计算（保证算法有足够数据）===
                        if len(ir_window) == 100:
                            # 转换为列表（算法需要）
                            ir_array = list(ir_window)
                            red_array = list(red_window)

                            # 调用算法
                            res = algo.process(ir_array, red_array)

                            # === 🔧 修复3：确保 quality 非负 ===
                            quality = max(0, res.get('quality', 0))

                            # 如果正在测量且数据有效，记录历史
                            if measurement_session["is_measuring"] and res['is_valid']:
                                measurement_session["hr_history"].append(res['hr'])
                                measurement_session["spo2_history"].append(res['spo2'])

                            # === 🔧 修复4：减少波形传输量（提高频率）===
                            # 只发送最后 5 个点（而不是全部），减少 WebSocket 负担
                            wave_data = ir_list[-5:] if len(ir_list) >= 5 else ir_list

                            # 构造数据包
                            payload = {
                                "wave": wave_data,
                                "hr": round(res['hr'], 1) if res['hr'] else 0,
                                "spo2": round(res['spo2'], 1) if res['spo2'] else 0,
                                "isValid": bool(res['is_valid']),
                                "q": round(quality, 2)  # 🔧 关键：确保 q 字段存在且非负
                            }

                            # 广播
                            if active_connections:
                                await asyncio.gather(
                                    *[ws.send_text(json.dumps(payload)) for ws in active_connections],
                                    return_exceptions=True
                                )

                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"❌ 处理错误: {e}")

            await asyncio.sleep(0.01)

    except Exception as e:
        print(f"❌ 串口错误: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(serial_worker())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/pulse")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    print(f"✅ WebSocket 连接，总数: {len(active_connections)}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"⚠️ WebSocket 断开，剩余: {len(active_connections)}")


@app.post("/api/pulse/start")
async def start_measurement():
    """开始测量"""
    measurement_session["is_measuring"] = True
    measurement_session["hr_history"] = []
    measurement_session["spo2_history"] = []

    algo.reset()

    print("🟢 开始测量")
    return {"msg": "测量已启动", "code": 200}


@app.post("/api/pulse/stop")
async def stop_and_report(user_id: int):
    """结束测量并返回报告"""
    measurement_session["is_measuring"] = False

    hr_list = measurement_session["hr_history"]
    spo2_list = measurement_session["spo2_history"]

    # 数据检查
    if len(hr_list) < 5:
        return {
            "code": 400,
            "msg": f"有效数据不足（{len(hr_list)}/5），请重新测量",
            "user_id": user_id,
            "avg_hr": 0,
            "avg_spo2": 0,
            "suggestion": "数据不足",
            "valid_rate": 0,
            "sample_count": 0
        }

    # 去除异常值
    def filter_outliers(data):
        if len(data) < 4:
            return data
        sorted_data = sorted(data)
        q1 = sorted_data[len(data) // 4]
        q3 = sorted_data[3 * len(data) // 4]
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        filtered = [x for x in data if lower <= x <= upper]
        return filtered if len(filtered) >= 3 else data

    hr_clean = filter_outliers(hr_list)
    spo2_clean = filter_outliers(spo2_list)

    # 计算平均值
    avg_hr = round(sum(hr_clean) / len(hr_clean), 1)
    avg_spo2 = round(sum(spo2_clean) / len(spo2_clean), 1)

    # 有效率
    valid_rate = round(len(hr_list) / max(len(hr_list), 1) * 100, 1)

    # 生成中医建议
    suggestion = generate_tcm_suggestion(avg_hr, avg_spo2)

    print(f"🟡 测量完成 - HR: {avg_hr}, SPO2: {avg_spo2}")

    return {
        "code": 200,
        "user_id": user_id,
        "avg_hr": avg_hr,
        "avg_spo2": avg_spo2,
        "suggestion": suggestion,
        "valid_rate": valid_rate,
        "sample_count": len(hr_clean),
        "measured_at": int(time.time())
    }


def generate_tcm_suggestion(hr, spo2):
    """生成中医建议"""
    lines = []

    if hr > 90:
        lines.append("【脉象】数脉（一息五至以上，脉来急促）")
        lines.append("【主病】多主热证。实热脉有力，虚热脉无力。")
        lines.append("【调养】宜清热降火，饮食清淡，可食绿豆汤、菊花茶。")
    elif hr < 60:
        lines.append("【脉象】迟脉（一息三至，脉来迟缓）")
        lines.append("【主病】多主寒证。寒邪凝滞或阳气不足。")
        lines.append("【调养】宜温阳散寒，可食生姜红糖水、羊肉汤。")
    else:
        lines.append("【脉象】缓脉（一息四至，不快不慢，从容和缓）")
        lines.append("【主病】平人脉象，气血调和。")

    if spo2 < 95:
        lines.append("【提示】血氧偏低，中医认为可能气虚血瘀。")
        lines.append("【调养】宜补气养血，可服黄芪、党参（需遵医嘱）。")

    return "\n".join(lines)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)