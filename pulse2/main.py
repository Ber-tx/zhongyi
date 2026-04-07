import asyncio
import json
import time
import math
import statistics
import serial
import numpy as np
import serial.tools.list_ports
from collections import deque
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.algorithm import PulseAlgorithm

# ===== 全局状态管理 =====
measurement_session = {
    "is_measuring": False,
    "hr_history": [],
    "spo2_history": [],
    "quality_history": [],
    "feature_history": [],
    "raw_ir": [],
    "raw_red": [],
    "total_windows": 0,
    "valid_windows": 0,
}

# 实例化算法
algo = PulseAlgorithm(buffer_size=100, fs=50)

# WebSocket 连接池
active_connections = set()

# 串口配置
BAUD_RATE = 115200


def auto_detect_serial_port():
    """
    自动检测串口。
    优先匹配常见芯片关键词（CH340、CP210x、Arduino 等），
    若无匹配则降级使用第一个可用串口，找不到返回 None。
    """
    KEYWORDS = ["CH340", "CP210", "Arduino", "USB Serial", "UART", "Silicon"]

    ports = serial.tools.list_ports.comports()
    if not ports:
        print("❌ 未找到任何串口设备，请检查连接")
        return None

    for port in ports:
        desc = (port.description or "") + (port.manufacturer or "")
        if any(kw.lower() in desc.lower() for kw in KEYWORDS):
            print(f"✅ 自动匹配串口: {port.device}  [{port.description}]")
            return port.device

    # 降级：取第一个串口
    fallback = ports[0]
    print(f"⚠️ 未匹配关键词，使用第一个可用串口: {fallback.device}  [{fallback.description}]")
    return fallback.device

# 🔧 关键修复：用滑动窗口累积数据
ir_window = deque(maxlen=100)
red_window = deque(maxlen=100)


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


def _safe_mean(values):
    return round(float(sum(values) / len(values)), 4) if values else 0.0


def _safe_std(values):
    if len(values) < 2:
        return 0.0
    return round(float(statistics.pstdev(values)), 4)


def extract_waveform_features(ir_signal, fs=50):
    """
    从单窗口IR波形提取脉搏相关特征。
    说明：仅用于增强脉象关联，不改变HR/SpO2主算法输出。
    """
    x = np.asarray(ir_signal, dtype=float)
    if len(x) < 8:
        return {
            "peak_count": 0,
            "interval_mean_ms": 0.0,
            "interval_sdnn_ms": 0.0,
            "interval_rmssd_ms": 0.0,
            "rhythm_cv": 0.0,
            "pulse_amp_mean": 0.0,
            "pulse_amp_cv": 0.0,
            "upstroke_time_ms": 0.0,
            "crest_factor": 0.0,
        }

    # 简单去中心，保留形态
    x = x - np.mean(x)
    std = float(np.std(x))
    if std <= 1e-9:
        return {
            "peak_count": 0,
            "interval_mean_ms": 0.0,
            "interval_sdnn_ms": 0.0,
            "interval_rmssd_ms": 0.0,
            "rhythm_cv": 0.0,
            "pulse_amp_mean": 0.0,
            "pulse_amp_cv": 0.0,
            "upstroke_time_ms": 0.0,
            "crest_factor": 0.0,
        }

    # 局部峰谷检测（不依赖外部峰值库）
    threshold_peak = np.mean(x) + 0.3 * std
    threshold_trough = np.mean(x) - 0.3 * std

    peaks = []
    troughs = []
    for i in range(1, len(x) - 1):
        if x[i - 1] < x[i] >= x[i + 1] and x[i] > threshold_peak:
            peaks.append(i)
        if x[i - 1] > x[i] <= x[i + 1] and x[i] < threshold_trough:
            troughs.append(i)

    intervals = []
    if len(peaks) >= 2:
        intervals = [((peaks[i] - peaks[i - 1]) / fs) for i in range(1, len(peaks))]

    intervals_ms = [v * 1000.0 for v in intervals]
    rr_diff = [intervals_ms[i] - intervals_ms[i - 1] for i in range(1, len(intervals_ms))]

    amplitudes = []
    upstroke_ms = []
    for p in peaks:
        prev_trough_candidates = [t for t in troughs if t < p]
        if not prev_trough_candidates:
            continue
        t = prev_trough_candidates[-1]
        amplitudes.append(float(x[p] - x[t]))
        upstroke_ms.append(float((p - t) / fs * 1000.0))

    interval_mean_ms = _safe_mean(intervals_ms)
    interval_sdnn_ms = _safe_std(intervals_ms)
    interval_rmssd_ms = round(math.sqrt(_safe_mean([d * d for d in rr_diff])), 4) if rr_diff else 0.0
    rhythm_cv = round((interval_sdnn_ms / interval_mean_ms), 4) if interval_mean_ms > 0 else 0.0
    pulse_amp_mean = _safe_mean(amplitudes)
    pulse_amp_cv = round((_safe_std(amplitudes) / pulse_amp_mean), 4) if pulse_amp_mean > 0 else 0.0
    upstroke_time_ms = _safe_mean(upstroke_ms)
    crest_factor = round(float(np.max(np.abs(x)) / (np.sqrt(np.mean(x ** 2)) + 1e-9)), 4)

    return {
        "peak_count": int(len(peaks)),
        "interval_mean_ms": interval_mean_ms,
        "interval_sdnn_ms": interval_sdnn_ms,
        "interval_rmssd_ms": interval_rmssd_ms,
        "rhythm_cv": rhythm_cv,
        "pulse_amp_mean": pulse_amp_mean,
        "pulse_amp_cv": pulse_amp_cv,
        "upstroke_time_ms": upstroke_time_ms,
        "crest_factor": crest_factor,
    }


def summarize_feature_history(feature_history):
    if not feature_history:
        return {
            "hrv_sdnn_ms": 0.0,
            "hrv_rmssd_ms": 0.0,
            "rhythm_cv": 0.0,
            "pulse_strength_index": 0.0,
            "pulse_amp_cv": 0.0,
            "upstroke_time_ms": 0.0,
            "perfusion_index": 0.0,
            "signal_quality": 0.0,
            "autocorr_ratio": 0.0,
        }

    def collect(key):
        vals = [f.get(key, 0.0) for f in feature_history if f.get("is_valid")]
        return vals if vals else [0.0]

    return {
        "hrv_sdnn_ms": round(_safe_mean(collect("interval_sdnn_ms")), 3),
        "hrv_rmssd_ms": round(_safe_mean(collect("interval_rmssd_ms")), 3),
        "rhythm_cv": round(_safe_mean(collect("rhythm_cv")), 4),
        "pulse_strength_index": round(_safe_mean(collect("pulse_amp_mean")), 4),
        "pulse_amp_cv": round(_safe_mean(collect("pulse_amp_cv")), 4),
        "upstroke_time_ms": round(_safe_mean(collect("upstroke_time_ms")), 3),
        "perfusion_index": round(_safe_mean(collect("perfusion_index")), 4),
        "signal_quality": round(_safe_mean(collect("quality")), 4),
        "autocorr_ratio": round(_safe_mean(collect("autocorr_ratio")), 4),
    }


def classify_pulse(avg_hr, feature_summary):
    tags = []

    if avg_hr > 90:
        tags.append("数脉倾向")
    elif avg_hr < 60:
        tags.append("迟脉倾向")
    else:
        tags.append("缓脉倾向")

    rhythm_cv = feature_summary.get("rhythm_cv", 0)
    if rhythm_cv <= 0.06:
        tags.append("节律较齐")
    elif rhythm_cv <= 0.12:
        tags.append("节律轻度不齐")
    else:
        tags.append("节律不齐倾向")

    perfusion_index = feature_summary.get("perfusion_index", 0)
    if perfusion_index < 0.8:
        tags.append("脉势偏弱")
    elif perfusion_index > 2.0:
        tags.append("脉势偏有力")
    else:
        tags.append("脉势中等")

    upstroke_ms = feature_summary.get("upstroke_time_ms", 0)
    if 0 < upstroke_ms < 120:
        tags.append("脉形偏紧促")
    elif upstroke_ms > 220:
        tags.append("脉形偏缓")

    return tags


async def serial_worker():
    """
    串口后台任务
    🔧 修复点：
    1. 用滑动窗口累积 100 个点
    2. 每次只发送少量波形点（减少传输量，提高频率）
    3. 确保 q 字段正确传递
    """
    serial_port = auto_detect_serial_port()
    if not serial_port:
        print("❌ 串口自动检测失败，后台任务退出")
        return

    print(f"🔄 串口已连接: {serial_port}, 算法采样率: 50Hz")

    try:
        ser = serial.Serial(serial_port, BAUD_RATE, timeout=0.1)

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

                            # 提取脉搏波形特征（增强脉诊语义）
                            waveform_features = extract_waveform_features(ir_array, fs=algo.FS)
                            perfusion_index = 0.0
                            if res.get("ir_mean", 0) > 0:
                                perfusion_index = (res.get("ir_rms", 0) / res.get("ir_mean", 1e-9)) * 100.0

                            feature_snapshot = {
                                "ts": int(time.time() * 1000),
                                "is_valid": bool(res.get("is_valid", False)),
                                "quality": round(float(quality), 3),
                                "autocorr_ratio": round(float(res.get("autocorr_ratio", 0.0)), 3),
                                "pearson_corr": round(float(res.get("pearson_corr", 0.0)), 3),
                                "perfusion_index": round(float(perfusion_index), 4),
                                **waveform_features,
                            }

                            if measurement_session["is_measuring"]:
                                measurement_session["total_windows"] += 1
                                measurement_session["quality_history"].append(round(float(quality), 3))
                                measurement_session["feature_history"].append(feature_snapshot)
                                measurement_session["raw_ir"].extend(ir_list)
                                measurement_session["raw_red"].extend(red_list)

                            # 如果正在测量且数据有效，记录历史
                            if measurement_session["is_measuring"] and res['is_valid']:
                                measurement_session["valid_windows"] += 1
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
    measurement_session["quality_history"] = []
    measurement_session["feature_history"] = []
    measurement_session["raw_ir"] = []
    measurement_session["raw_red"] = []
    measurement_session["total_windows"] = 0
    measurement_session["valid_windows"] = 0

    algo.reset()

    print("🟢 开始测量")
    return {"msg": "测量已启动", "code": 200}


@app.post("/api/pulse/stop")
async def stop_and_report(user_id: int):
    """结束测量并返回报告"""
    measurement_session["is_measuring"] = False

    hr_list = measurement_session["hr_history"]
    spo2_list = measurement_session["spo2_history"]
    total_windows = measurement_session["total_windows"]
    valid_windows = measurement_session["valid_windows"]
    feature_history = measurement_session["feature_history"]
    raw_ir = measurement_session["raw_ir"]
    raw_red = measurement_session["raw_red"]

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
            "sample_count": 0,
            "pulse_metrics": {},
            "pulse_tags": [],
        }

    hr_clean = filter_outliers(hr_list)
    spo2_clean = filter_outliers(spo2_list)

    # 计算平均值
    avg_hr = round(sum(hr_clean) / len(hr_clean), 1)
    avg_spo2 = round(sum(spo2_clean) / len(spo2_clean), 1)

    # 有效率
    valid_rate = round((valid_windows / max(total_windows, 1)) * 100, 1)

    # 脉搏特征汇总
    pulse_metrics = summarize_feature_history(feature_history)
    pulse_tags = classify_pulse(avg_hr, pulse_metrics)

    # key_metrics_json：切诊落库/喂给LLM的最小关键指标集。
    # hrv_rmssd_ms=窗口间脉搏间期RMSSD(ms)，rhythm_cv=节律变异系数，perfusion_index=灌注指数，
    # signal_quality=信号质量评分，pulse_tags=基于HR/节律/PI的脉象标签。
    key_metrics = {
        "hrv_rmssd_ms": pulse_metrics.get("hrv_rmssd_ms", 0.0),
        "rhythm_cv": pulse_metrics.get("rhythm_cv", 0.0),
        "perfusion_index": pulse_metrics.get("perfusion_index", 0.0),
        "signal_quality": pulse_metrics.get("signal_quality", 0.0),
        "pulse_tags": pulse_tags,
    }

    # 生成中医建议
    suggestion = generate_tcm_suggestion(avg_hr, avg_spo2, pulse_metrics, pulse_tags)

    # raw_data_json：前端详细模式直接转发给大模型的完整脉诊上下文。
    # fs=采样率，buffer_size=单窗长度，raw_ir/raw_red=原始波形，window_features=每窗特征，
    # summary_metrics=会话汇总指标，pulse_tags=最终脉象标签。
    raw_data_json = {
        "fs": algo.FS,
        "buffer_size": algo.BUFFER_SIZE,
        "raw_ir": raw_ir,
        "raw_red": raw_red,
        "window_features": feature_history,
        "summary_metrics": pulse_metrics,
        "pulse_tags": pulse_tags,
    }

    print(f"🟡 测量完成 - HR: {avg_hr}, SPO2: {avg_spo2}")

    return {
        "code": 200,
        "user_id": user_id,
        "avg_hr": avg_hr,
        "avg_spo2": avg_spo2,
        "suggestion": suggestion,
        "valid_rate": valid_rate,
        "sample_count": len(hr_clean),
        "measured_at": int(time.time()),
        "pulse_metrics": pulse_metrics,
        "pulse_tags": pulse_tags,
        "key_metrics_json": json.dumps(key_metrics, ensure_ascii=False),
        "raw_data_json": json.dumps(raw_data_json, ensure_ascii=False)
    }


def generate_tcm_suggestion(hr, spo2, pulse_metrics=None, pulse_tags=None):
    """生成中医建议"""
    lines = []
    pulse_metrics = pulse_metrics or {}
    pulse_tags = pulse_tags or []

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

    if pulse_tags:
        lines.append("【脉搏特征】" + "、".join(pulse_tags))

    hrv_rmssd = pulse_metrics.get("hrv_rmssd_ms", 0)
    rhythm_cv = pulse_metrics.get("rhythm_cv", 0)
    perfusion_index = pulse_metrics.get("perfusion_index", 0)

    lines.append(
        f"【量化摘要】RMSSD={hrv_rmssd}ms，节律CV={rhythm_cv}，灌注指数PI={perfusion_index}%。"
    )

    if rhythm_cv > 0.12:
        lines.append("【提示】节律波动偏大，建议静息后复测，并结合临床心电评估。")

    return "\n".join(lines)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)