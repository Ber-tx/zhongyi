import asyncio
import json
import time
import serial
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 导入上面的算法和模型
from core.algorithm import PulseAlgorithm
from models.schemas import PulseReport

# ===== 全局状态管理 =====
# 用于存储当前测量过程中的有效数据，以便最后计算平均值
measurement_session = {
    "is_measuring": False,  # 是否正在进行正式测量（前端点开始后为True）
    "hr_history": [],  # 存放心率历史
    "spo2_history": [],  # 存放血氧历史
    "raw_wave_buffer": []  # 存放原始波形（可选，用于中医分析）
}

# 实例化算法
algo = PulseAlgorithm()
active_connections = set()

# 配置串口
SERIAL_PORT = "COM8"  # 你的端口
BAUD_RATE = 115200


# ===== 后台任务 =====
async def serial_worker():
    # 关键：实例化算法时必须匹配 50Hz
    algo = PulseAlgorithm(buffer_size=100, fs=50)
    print(f"🔄 串口已连接，算法采样率设定为 50Hz")

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

                        # 循环处理这一小包数据
                        res = {"hr": 0, "spo2": 0, "is_valid": False, "quality": 0}
                        for i in range(len(ir_list)):
                            # 喂入算法
                            res = algo.process(ir_list[i], red_list[i])

                        payload = {
                            "wave": [int(x) for x in ir_list],
                            "hr": float(res['hr']) if res['hr'] else 0.0,
                            "spo2": float(res['spo2']) if res['spo2'] else 0.0,
                            "isValid": bool(res['is_valid']),
                            "q": float(res['quality'])
                        }

                        if measurement_session["is_measuring"] and res['is_valid']:
                            measurement_session["hr_history"].append(res['hr'])
                            measurement_session["spo2_history"].append(res['spo2'])

                        if active_connections:
                            await asyncio.gather(*[ws.send_text(json.dumps(payload)) for ws in active_connections])

                except Exception as e:
                    print(f"Err: {e}")
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"Serial Error: {e}")

# ===== 生命周期管理 (替代 deprecated 的 on_event) =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    task = asyncio.create_task(serial_worker())
    yield
    # 关闭时
    task.cancel()


app = FastAPI(lifespan=lifespan)

# 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 接口定义 =====

@app.websocket("/ws/pulse")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # 保持连接
    except WebSocketDisconnect:
        active_connections.remove(websocket)


@app.post("/api/pulse/start")
async def start_measurement():
    """ Vue3 点击'开始测量'时调用，重置历史数据 """
    measurement_session["is_measuring"] = True
    measurement_session["hr_history"] = []
    measurement_session["spo2_history"] = []
    measurement_session["raw_wave_buffer"] = []
    algo.reset()  # 重置算法内部状态
    return {"msg": "Started"}


@app.post("/api/pulse/stop")
async def stop_and_report(user_id: int):
    """ Vue3 点击'结束/保存'时调用，计算平均值并返回 """
    measurement_session["is_measuring"] = False

    hr_list = measurement_session["hr_history"]
    spo2_list = measurement_session["spo2_history"]

    # 计算平均值 (排除空列表情况)
    avg_hr = round(sum(hr_list) / len(hr_list), 1) if hr_list else 0
    avg_spo2 = round(sum(spo2_list) / len(spo2_list), 1) if spo2_list else 0

    # 简单的中医建议生成
    suggestion = "脉象平稳，气血调和。"
    if avg_hr > 90:
        suggestion = "脉数，多主热证。"
    elif avg_hr > 0 and avg_hr < 60:
        suggestion = "脉迟，多主寒证或气虚。"
    elif not hr_list:
        suggestion = "测量数据不足或信号干扰严重，建议重测。"

    report = PulseReport(
        user_id=user_id,
        avg_hr=avg_hr,
        avg_spo2=avg_spo2,
        # 将原始波形转为JSON字符串存库，这里只存了部分波形
        raw_data_json=json.dumps(measurement_session["raw_wave_buffer"]),
        suggestion=suggestion,
        measured_at=int(time.time())
    )

    return report


if __name__ == "__main__":
    import uvicorn

    # 注意：直接运行 main.py 时使用
    uvicorn.run(app, host="0.0.0.0", port=8000)