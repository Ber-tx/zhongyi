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

# =====================================================================
# 全局状态管理
# =====================================================================
measurement_session = {
    "is_measuring":    False,
    "hr_history":      [],
    "spo2_history":    [],
    "quality_history": [],
    "feature_history": [],
    "raw_ir":          [],
    "raw_red":         [],
    "total_windows":   0,
    "valid_windows":   0,
}

algo = PulseAlgorithm(buffer_size=100, fs=50)
active_connections = set()

# ── 串口 ──────────────────────────────────────────────────────────────
BAUD_RATE = 115200

# ── 算法步进 ──────────────────────────────────────────────────────────
# 每积累 N 个新样本后运行一次算法窗口
# 50Hz 采样 → ALGO_STEP_SAMPLES=5 → 约 100ms 刷新一次（更平滑的实时 HR 估算）
ALGO_STEP_SAMPLES = 5

# ── WebSocket 推送节拍 ────────────────────────────────────────────────
#
# 设计目标：前端以 50Hz 的速度消耗波形点，示波器风格不卡顿
#
# 数学推导：
#   采样率                    = 50 Hz  → 每点间隔 20 ms
#   WS 推送间隔               = 20 ms  → 25 次/s（requestAnimationFrame ≈ 60fps，
#                                         前端用分数累加器按时间消耗，完全解耦）
#   每包携带点数              = 2 pts
#   总吞吐                    = 2 × 50 = 100 pts/s ... 等等
#
#   正确推导：
#   WS_PUSH_INTERVAL = 0.040 s  → 25 pushes/s
#   WS_BASE_POINTS   = 2 pts/push
#   → 实际传输速率   = 25 × 2 = 50 pts/s ✓ 完全匹配采样率
#
#   前端分数累加器：每帧消耗 Δt × 50 pts → 无论帧率高低都精确
#
WS_PUSH_INTERVAL       = 0.040   # 25Hz 推送节拍（秒）
WS_BASE_POINTS_PER_PUSH = 2      # 基础每包点数 → 25 × 2 = 50 pts/s
WS_MAX_BATCH_POINTS    = 6       # 积压时最多补发点数上限（不超过此值避免前端爆帧）
SIGNAL_VALID_THRESHOLD = 0.45    # 低于此值认为手指未接触


def auto_detect_serial_port():
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
    fallback = ports[0]
    print(f"⚠️ 未匹配关键词，降级使用: {fallback.device}  [{fallback.description}]")
    return fallback.device


# 滑动算法窗口（固定 100 点 = 2 秒）
ir_window  = deque(maxlen=100)
red_window = deque(maxlen=100)


# ── 统计工具 ──────────────────────────────────────────────────────────
def filter_outliers(data):
    if len(data) < 4:
        return data
    s = sorted(data)
    q1, q3 = s[len(data) // 4], s[3 * len(data) // 4]
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    filtered = [x for x in data if lo <= x <= hi]
    return filtered if len(filtered) >= 3 else data


def _safe_mean(v):
    return round(float(sum(v) / len(v)), 4) if v else 0.0


def _safe_std(v):
    return round(float(statistics.pstdev(v)), 4) if len(v) >= 2 else 0.0


# ── 波形特征提取 ──────────────────────────────────────────────────────
def extract_waveform_features(ir_signal, fs=50):
    x = np.asarray(ir_signal, dtype=float)
    if len(x) < 8:
        return _empty_features()

    x -= np.mean(x)
    std = float(np.std(x))
    if std <= 1e-9:
        return _empty_features()

    thr_peak   = np.mean(x) + 0.3 * std
    thr_trough = np.mean(x) - 0.3 * std

    peaks, troughs = [], []
    for i in range(1, len(x) - 1):
        if x[i - 1] < x[i] >= x[i + 1] and x[i] > thr_peak:
            peaks.append(i)
        if x[i - 1] > x[i] <= x[i + 1] and x[i] < thr_trough:
            troughs.append(i)

    intervals_ms = [(peaks[i] - peaks[i - 1]) / fs * 1000.0
                    for i in range(1, len(peaks))] if len(peaks) >= 2 else []
    rr_diff = [intervals_ms[i] - intervals_ms[i - 1]
               for i in range(1, len(intervals_ms))]

    amplitudes, upstroke_ms = [], []
    for p in peaks:
        prev = [t for t in troughs if t < p]
        if not prev:
            continue
        t = prev[-1]
        amplitudes.append(float(x[p] - x[t]))
        upstroke_ms.append(float((p - t) / fs * 1000.0))

    im  = _safe_mean(intervals_ms)
    isd = _safe_std(intervals_ms)
    rmssd = round(math.sqrt(_safe_mean([d * d for d in rr_diff])), 4) if rr_diff else 0.0
    return {
        "peak_count":         int(len(peaks)),
        "interval_mean_ms":   im,
        "interval_sdnn_ms":   isd,
        "interval_rmssd_ms":  rmssd,
        "rhythm_cv":          round(isd / im, 4) if im > 0 else 0.0,
        "pulse_amp_mean":     _safe_mean(amplitudes),
        "pulse_amp_cv":       round(_safe_std(amplitudes) / _safe_mean(amplitudes), 4)
                              if _safe_mean(amplitudes) > 0 else 0.0,
        "upstroke_time_ms":   _safe_mean(upstroke_ms),
        "crest_factor":       round(float(np.max(np.abs(x)) /
                              (np.sqrt(np.mean(x ** 2)) + 1e-9)), 4),
    }


def _empty_features():
    return {k: 0 for k in [
        "peak_count", "interval_mean_ms", "interval_sdnn_ms",
        "interval_rmssd_ms", "rhythm_cv", "pulse_amp_mean",
        "pulse_amp_cv", "upstroke_time_ms", "crest_factor"
    ]}


def summarize_feature_history(feature_history):
    if not feature_history:
        return {k: 0.0 for k in [
            "hrv_sdnn_ms", "hrv_rmssd_ms", "rhythm_cv", "pulse_strength_index",
            "pulse_amp_cv", "upstroke_time_ms", "perfusion_index",
            "signal_quality", "autocorr_ratio"
        ]}

    def collect(key):
        vals = [f.get(key, 0.0) for f in feature_history if f.get("is_valid")]
        return vals or [0.0]

    return {
        "hrv_sdnn_ms":          round(_safe_mean(collect("interval_sdnn_ms")), 3),
        "hrv_rmssd_ms":         round(_safe_mean(collect("interval_rmssd_ms")), 3),
        "rhythm_cv":            round(_safe_mean(collect("rhythm_cv")), 4),
        "pulse_strength_index": round(_safe_mean(collect("pulse_amp_mean")), 4),
        "pulse_amp_cv":         round(_safe_mean(collect("pulse_amp_cv")), 4),
        "upstroke_time_ms":     round(_safe_mean(collect("upstroke_time_ms")), 3),
        "perfusion_index":      round(_safe_mean(collect("perfusion_index")), 4),
        "signal_quality":       round(_safe_mean(collect("quality")), 4),
        "autocorr_ratio":       round(_safe_mean(collect("autocorr_ratio")), 4),
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

    pi = feature_summary.get("perfusion_index", 0)
    if pi < 0.8:
        tags.append("脉势偏弱")
    elif pi > 2.0:
        tags.append("脉势偏有力")
    else:
        tags.append("脉势中等")

    upstroke = feature_summary.get("upstroke_time_ms", 0)
    if 0 < upstroke < 120:
        tags.append("脉形偏紧促")
    elif upstroke > 220:
        tags.append("脉形偏缓")

    return tags


# =====================================================================
# 串口后台任务
#
# 速率匹配总结：
#   串口 → 50Hz 采样（原始）
#   算法 → 每 5 个新样本运行一次（≈10Hz，更频繁的实时 HR 更新）
#   WS   → 每 40ms 推送 2 点（25Hz × 2 = 50pts/s = 采样率 ✓）
#   前端 → requestAnimationFrame + 分数累加器精确消耗 50pts/s
# =====================================================================
async def serial_worker():
    serial_port = auto_detect_serial_port()
    if not serial_port:
        print("❌ 串口自动检测失败，后台任务退出")
        return

    print(f"🔄 串口已连接: {serial_port} | 采样率: 50Hz | WS: 25Hz×2pts=50pts/s")

    try:
        ser = serial.Serial(serial_port, BAUD_RATE, timeout=0.1)

        # 待推送波形点队列（maxlen 防止无限积压）
        pending_wave: deque = deque(maxlen=300)

        new_samples_since_algo = 0
        last_ws_push_ts        = 0.0
        last_algo_snapshot     = {"hr": 0.0, "spo2": 0.0, "is_valid": False, "quality": 0.0}

        # 性能统计（每 5 秒打印一次）
        perf_t0      = time.perf_counter()
        perf_serial  = 0
        perf_algo    = 0
        perf_ws      = 0

        while True:
            if ser.in_waiting:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()

                    if not line.startswith('{"ir":'):
                        await asyncio.sleep(0.001)
                        continue

                    data     = json.loads(line)
                    ir_list  = data['ir']
                    red_list = data['red']
                    perf_serial += len(ir_list)

                    # 更新滑动算法窗口
                    for v_ir, v_red in zip(ir_list, red_list):
                        ir_window.append(v_ir)
                        red_window.append(v_red)

                    # 加入待推送队列（原始 IR 值供前端示波器显示）
                    pending_wave.extend(ir_list)

                    # 记录到 session
                    if measurement_session["is_measuring"]:
                        measurement_session["raw_ir"].extend(ir_list)
                        measurement_session["raw_red"].extend(red_list)

                    new_samples_since_algo += len(ir_list)

                    # ── 算法窗口：每 5 个新样本触发一次 ──────────────────────
                    if len(ir_window) == 100 and new_samples_since_algo >= ALGO_STEP_SAMPLES:
                        new_samples_since_algo = 0
                        perf_algo += 1

                        ir_arr  = list(ir_window)
                        red_arr = list(red_window)
                        res     = algo.process(ir_arr, red_arr)

                        quality = max(0.0, float(res.get('quality', 0)))

                        # 计算灌注指数
                        perfusion_index = 0.0
                        ir_mean = res.get("ir_mean", 0)
                        if ir_mean > 0:
                            perfusion_index = (res.get("ir_rms", 0) / (ir_mean + 1e-9)) * 100.0

                        # 波形特征提取
                        wf = extract_waveform_features(ir_arr, fs=algo.FS)

                        feature_snapshot = {
                            "ts":              int(time.time() * 1000),
                            "is_valid":        bool(res.get("is_valid", False)),
                            "quality":         round(quality, 3),
                            "autocorr_ratio":  round(float(res.get("autocorr_ratio", 0.0)), 3),
                            "pearson_corr":    round(float(res.get("pearson_corr", 0.0)), 3),
                            "perfusion_index": round(float(perfusion_index), 4),
                            **wf,
                        }

                        if measurement_session["is_measuring"]:
                            measurement_session["total_windows"] += 1
                            measurement_session["quality_history"].append(round(quality, 3))
                            measurement_session["feature_history"].append(feature_snapshot)

                            if res['is_valid']:
                                measurement_session["valid_windows"] += 1
                                measurement_session["hr_history"].append(res['hr'])
                                measurement_session["spo2_history"].append(res['spo2'])

                        is_valid = bool(res['is_valid']) and quality > SIGNAL_VALID_THRESHOLD
                        last_algo_snapshot = {
                            "hr":       round(res['hr'],   1) if is_valid and res['hr']   else 0,
                            "spo2":     round(res['spo2'], 1) if is_valid and res['spo2'] else 0,
                            "is_valid": is_valid,
                            "quality":  round(quality, 2),
                        }

                    # ── WebSocket 推送（固定节拍 40ms） ───────────────────────
                    now = time.perf_counter()
                    if active_connections and (now - last_ws_push_ts) >= WS_PUSH_INTERVAL and pending_wave:
                        # 积压补偿：正常 2 点，最多 WS_MAX_BATCH_POINTS 点
                        # 积压超过 60 点时才触发补发，避免过度推送造成前端爆帧
                        backlog = len(pending_wave)
                        extra   = min(2, backlog // 60) if backlog > 60 else 0
                        batch_n = min(
                            backlog,
                            WS_BASE_POINTS_PER_PUSH + extra,
                            WS_MAX_BATCH_POINTS
                        )

                        wave_data = [pending_wave.popleft() for _ in range(batch_n)]
                        last_ws_push_ts = now
                        perf_ws += 1

                        payload_text = json.dumps({
                            "wave":    wave_data,
                            "hr":      last_algo_snapshot["hr"],
                            "spo2":    last_algo_snapshot["spo2"],
                            "isValid": last_algo_snapshot["is_valid"],
                            "q":       last_algo_snapshot["quality"]
                        })

                        stale = []
                        for ws in list(active_connections):
                            try:
                                await ws.send_text(payload_text)
                            except Exception:
                                stale.append(ws)
                        for ws in stale:
                            active_connections.discard(ws)

                    # ── 性能统计 ──────────────────────────────────────────────
                    elapsed = now - perf_t0
                    if elapsed >= 5.0:
                        print(
                            f"📈 速率统计 | serial={perf_serial / elapsed:.1f} pts/s "
                            f"| algo={perf_algo / elapsed:.1f} Hz "
                            f"| ws={perf_ws / elapsed:.1f} Hz "
                            f"| clients={len(active_connections)} "
                            f"| pending={len(pending_wave)} pts"
                        )
                        perf_t0 = now; perf_serial = perf_algo = perf_ws = 0

                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"❌ 处理错误: {e}")

            await asyncio.sleep(0.002)

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
        active_connections.discard(websocket)
        print(f"⚠️ WebSocket 断开，剩余: {len(active_connections)}")


@app.post("/api/pulse/start")
async def start_measurement():
    measurement_session.update({
        "is_measuring":    True,
        "hr_history":      [],
        "spo2_history":    [],
        "quality_history": [],
        "feature_history": [],
        "raw_ir":          [],
        "raw_red":         [],
        "total_windows":   0,
        "valid_windows":   0,
    })
    algo.reset()
    print("🟢 测量开始")
    return {"msg": "测量已启动", "code": 200}


@app.post("/api/pulse/stop")
async def stop_and_report(user_id: int):
    measurement_session["is_measuring"] = False

    hr_list        = measurement_session["hr_history"]
    spo2_list      = measurement_session["spo2_history"]
    total_windows  = measurement_session["total_windows"]
    valid_windows  = measurement_session["valid_windows"]
    feature_history = measurement_session["feature_history"]
    raw_ir         = measurement_session["raw_ir"]
    raw_red        = measurement_session["raw_red"]

    if len(hr_list) < 5:
        return {
            "code": 400,
            "msg":  f"有效数据不足（{len(hr_list)}/5），请重新测量",
            "user_id": user_id,
            "avg_hr": 0, "avg_spo2": 0,
            "suggestion": "数据不足",
            "valid_rate": 0, "sample_count": 0,
            "pulse_metrics": {}, "pulse_tags": [],
        }

    hr_clean   = filter_outliers(hr_list)
    spo2_clean = filter_outliers(spo2_list)
    avg_hr     = round(sum(hr_clean) / len(hr_clean), 1)
    avg_spo2   = round(sum(spo2_clean) / len(spo2_clean), 1)
    valid_rate = round((valid_windows / max(total_windows, 1)) * 100, 1)

    pulse_metrics = summarize_feature_history(feature_history)
    pulse_tags    = classify_pulse(avg_hr, pulse_metrics)
    suggestion    = generate_tcm_suggestion(avg_hr, avg_spo2, pulse_metrics, pulse_tags)

    key_metrics = {
        "hrv_rmssd_ms":    pulse_metrics.get("hrv_rmssd_ms", 0.0),
        "rhythm_cv":       pulse_metrics.get("rhythm_cv", 0.0),
        "perfusion_index": pulse_metrics.get("perfusion_index", 0.0),
        "signal_quality":  pulse_metrics.get("signal_quality", 0.0),
        "pulse_tags":      pulse_tags,
    }
    raw_data_json = {
        "fs":              algo.FS,
        "buffer_size":     algo.BUFFER_SIZE,
        "raw_ir":          raw_ir,
        "raw_red":         raw_red,
        "window_features": feature_history,
        "summary_metrics": pulse_metrics,
        "pulse_tags":      pulse_tags,
    }

    print(f"🟡 测量完成 | HR: {avg_hr} bpm | SpO2: {avg_spo2}% | 有效率: {valid_rate}%")

    return {
        "code":           200,
        "user_id":        user_id,
        "avg_hr":         avg_hr,
        "avg_spo2":       avg_spo2,
        "suggestion":     suggestion,
        "valid_rate":     valid_rate,
        "sample_count":   len(hr_clean),
        "measured_at":    int(time.time()),
        "pulse_metrics":  pulse_metrics,
        "pulse_tags":     pulse_tags,
        "key_metrics_json":  json.dumps(key_metrics, ensure_ascii=False),
        "raw_data_json":     json.dumps(raw_data_json, ensure_ascii=False),
    }


def generate_tcm_suggestion(hr, spo2, pulse_metrics=None, pulse_tags=None):
    lines = []
    pulse_metrics = pulse_metrics or {}
    pulse_tags    = pulse_tags    or []

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

    hrv_rmssd      = pulse_metrics.get("hrv_rmssd_ms", 0)
    rhythm_cv      = pulse_metrics.get("rhythm_cv", 0)
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