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
    "started_at":      None,
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
MIN_MEASURE_SECONDS    = 45      # 最小测量时长（秒）
MIN_VALID_WINDOWS      = 20      # 最小有效算法窗口数
MIN_VALID_RATE         = 60.0    # 最低有效窗口占比（%）


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


def _robust_center(v):
    if not v:
        return 0.0
    if len(v) < 5:
        return _safe_mean(v)
    s = sorted(float(x) for x in v)
    trim = max(1, int(len(s) * 0.1))
    core = s[trim:len(s) - trim] if len(s) - 2 * trim >= 1 else s
    return round(float(sum(core) / len(core)), 4)


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

    # 使用最小峰间距抑制噪声双峰（50Hz 下约 350ms，不可能出现生理性双峰）
    peaks, troughs = [], []
    min_peak_distance = max(1, int(0.35 * fs))
    last_peak_idx = -min_peak_distance

    for i in range(1, len(x) - 1):
        is_peak = x[i - 1] < x[i] >= x[i + 1] and x[i] > thr_peak
        if is_peak:
            if (i - last_peak_idx) >= min_peak_distance:
                peaks.append(i)
                last_peak_idx = i
            elif peaks and x[i] > x[peaks[-1]]:
                peaks[-1] = i
                last_peak_idx = i
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
        vals = [
            f.get(key, 0.0)
            for f in feature_history
            if f.get("is_valid")
            and f.get("quality", 0.0) >= 0.80
            and f.get("autocorr_ratio", 0.0) >= 0.50
        ]
        return vals or [0.0]

    return {
        "hrv_sdnn_ms":          round(_robust_center(collect("interval_sdnn_ms")), 3),
        "hrv_rmssd_ms":         round(_robust_center(collect("interval_rmssd_ms")), 3),
        "rhythm_cv":            round(_robust_center(collect("rhythm_cv")), 4),
        "pulse_strength_index": round(_robust_center(collect("pulse_amp_mean")), 4),
        "pulse_amp_cv":         round(_robust_center(collect("pulse_amp_cv")), 4),
        "upstroke_time_ms":     round(_robust_center(collect("upstroke_time_ms")), 3),
        "perfusion_index":      round(_robust_center(collect("perfusion_index")), 4),
        "signal_quality":       round(_robust_center(collect("quality")), 4),
        "autocorr_ratio":       round(_robust_center(collect("autocorr_ratio")), 4),
    }


def infer_pulse_pattern(avg_hr, feature_summary):
    scores = {
        "数脉倾向": 0.0,
        "迟脉倾向": 0.0,
        "缓脉倾向": 0.0,
    }
    evidence = []

    rhythm_cv = float(feature_summary.get("rhythm_cv", 0.0))
    rmssd = float(feature_summary.get("hrv_rmssd_ms", 0.0))
    sdnn = float(feature_summary.get("hrv_sdnn_ms", 0.0))
    pi = float(feature_summary.get("perfusion_index", 0.0))
    upstroke = float(feature_summary.get("upstroke_time_ms", 0.0))
    quality = float(feature_summary.get("signal_quality", 0.0))
    autocorr = float(feature_summary.get("autocorr_ratio", 0.0))

    # HR 仅作为一项证据，降低其权重，避免单指标主导结论
    if avg_hr >= 95:
        scores["数脉倾向"] += 1.4
        evidence.append(f"心率偏快({avg_hr}bpm)")
    elif avg_hr <= 55:
        scores["迟脉倾向"] += 1.4
        evidence.append(f"心率偏慢({avg_hr}bpm)")
    else:
        scores["缓脉倾向"] += 1.2
        evidence.append(f"心率中段({avg_hr}bpm)")

    # 节律证据
    if rhythm_cv > 0.12:
        scores["数脉倾向"] += 0.9
        evidence.append(f"节律波动偏大(CV={rhythm_cv})")
    elif rhythm_cv <= 0.06:
        scores["缓脉倾向"] += 0.8
        evidence.append(f"节律较齐(CV={rhythm_cv})")
    else:
        scores["缓脉倾向"] += 0.4

    # HRV 证据（仅在信号较好时计入）
    if quality >= 0.85 and autocorr >= 0.55:
        if rmssd >= 55 or sdnn >= 50:
            scores["数脉倾向"] += 0.6
            evidence.append(f"HRV偏高(RMSSD={rmssd}ms, SDNN={sdnn}ms)")
        elif rmssd <= 20 and sdnn <= 20:
            scores["缓脉倾向"] += 0.5
            evidence.append(f"HRV偏低(RMSSD={rmssd}ms, SDNN={sdnn}ms)")

    # 脉势与上升支证据
    if pi < 0.8:
        scores["迟脉倾向"] += 0.5
        evidence.append(f"灌注偏弱(PI={pi})")
    elif pi > 2.0:
        scores["数脉倾向"] += 0.5
        evidence.append(f"灌注偏强(PI={pi})")
    else:
        scores["缓脉倾向"] += 0.2

    if 0 < upstroke < 120:
        scores["数脉倾向"] += 0.5
        evidence.append(f"上升支偏快({upstroke}ms)")
    elif upstroke > 220:
        scores["迟脉倾向"] += 0.5
        evidence.append(f"上升支偏慢({upstroke}ms)")

    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    primary_label, primary_score = ordered[0]
    secondary_label, secondary_score = ordered[1]
    score_gap = round(primary_score - secondary_score, 3)

    return {
        "scores": {k: round(v, 3) for k, v in scores.items()},
        "primary": primary_label,
        "secondary": secondary_label,
        "score_gap": score_gap,
        "evidence": evidence,
    }


def classify_pulse(avg_hr, feature_summary, confidence_level="medium"):
    if confidence_level == "low":
        return ["信号可信度偏低，当前仅供参考"]

    fusion = infer_pulse_pattern(avg_hr, feature_summary)

    tags = []
    if fusion["score_gap"] < 0.35:
        tags.append("脉象倾向不单一（需结合临床）")
    tags.append(fusion["primary"])

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

    tags.extend([f"证据:{ev}" for ev in fusion["evidence"][:3]])

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
        "started_at":      time.time(),
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
    started_at     = measurement_session.get("started_at")
    feature_history = measurement_session["feature_history"]
    raw_ir         = measurement_session["raw_ir"]
    raw_red        = measurement_session["raw_red"]
    duration_sec   = int(time.time() - started_at) if started_at else 0
    valid_rate     = round((valid_windows / max(total_windows, 1)) * 100, 1)

    if len(hr_list) < 5:
        return {
            "code": 400,
            "msg":  f"有效数据不足（{len(hr_list)}/5），请重新测量",
            "user_id": user_id,
            "avg_hr": 0, "avg_spo2": 0,
            "suggestion": "数据不足",
            "valid_rate": 0, "sample_count": 0,
            "duration_sec": duration_sec,
            "pulse_metrics": {}, "pulse_tags": [],
        }

    if duration_sec < MIN_MEASURE_SECONDS or valid_windows < MIN_VALID_WINDOWS or valid_rate < MIN_VALID_RATE:
        return {
            "code": 400,
            "msg": (
                "测量质量未达报告标准，请保持静止并持续测量后重试。"
                f" 当前时长={duration_sec}s（要求≥{MIN_MEASURE_SECONDS}s），"
                f" 有效窗口={valid_windows}（要求≥{MIN_VALID_WINDOWS}），"
                f" 有效率={valid_rate}%（要求≥{MIN_VALID_RATE}%）。"
            ),
            "user_id": user_id,
            "avg_hr": 0,
            "avg_spo2": 0,
            "suggestion": "测量质量不足",
            "valid_rate": valid_rate,
            "sample_count": len(hr_list),
            "duration_sec": duration_sec,
            "pulse_metrics": {},
            "pulse_tags": [],
        }

    hr_clean   = filter_outliers(hr_list)
    spo2_clean = filter_outliers(spo2_list)
    avg_hr     = round(sum(hr_clean) / len(hr_clean), 1)
    avg_spo2   = round(sum(spo2_clean) / len(spo2_clean), 1)

    pulse_metrics = summarize_feature_history(feature_history)
    confidence   = evaluate_measurement_confidence(valid_rate, len(hr_clean), duration_sec, pulse_metrics)
    fusion_result = infer_pulse_pattern(avg_hr, pulse_metrics)
    pulse_tags   = classify_pulse(avg_hr, pulse_metrics, confidence_level=confidence["level"])
    suggestion    = generate_tcm_suggestion(
        avg_hr,
        avg_spo2,
        pulse_metrics,
        pulse_tags,
        fusion_primary=fusion_result["primary"],
        fusion_gap=fusion_result["score_gap"],
        fusion_scores=fusion_result["scores"],
    )

    key_metrics = {
        "hrv_rmssd_ms":    pulse_metrics.get("hrv_rmssd_ms", 0.0),
        "rhythm_cv":       pulse_metrics.get("rhythm_cv", 0.0),
        "perfusion_index": pulse_metrics.get("perfusion_index", 0.0),
        "signal_quality":  pulse_metrics.get("signal_quality", 0.0),
        "fusion_primary": fusion_result["primary"],
        "fusion_secondary": fusion_result["secondary"],
        "fusion_score_gap": fusion_result["score_gap"],
        "fusion_scores": fusion_result["scores"],
        "confidence_score": confidence["score"],
        "confidence_level": confidence["level"],
        "confidence_reasons": confidence["reasons"],
        "pulse_tags":      pulse_tags,
    }
    raw_data_json = {
        "fs":              algo.FS,
        "buffer_size":     algo.BUFFER_SIZE,
        "raw_ir":          raw_ir,
        "raw_red":         raw_red,
        "window_features": feature_history,
        "summary_metrics": pulse_metrics,
        "fusion_result": fusion_result,
        "measurement_confidence": confidence,
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
        "duration_sec":   duration_sec,
        "fusion_primary": fusion_result["primary"],
        "fusion_secondary": fusion_result["secondary"],
        "fusion_score_gap": fusion_result["score_gap"],
        "fusion_scores": fusion_result["scores"],
        "confidence_score": confidence["score"],
        "confidence_level": confidence["level"],
        "confidence_reasons": confidence["reasons"],
        "measured_at":    int(time.time()),
        "pulse_metrics":  pulse_metrics,
        "pulse_tags":     pulse_tags,
        "key_metrics_json":  json.dumps(key_metrics, ensure_ascii=False),
        "raw_data_json":     json.dumps(raw_data_json, ensure_ascii=False),
    }


def generate_tcm_suggestion(
    hr,
    spo2,
    pulse_metrics=None,
    pulse_tags=None,
    fusion_primary=None,
    fusion_gap=0.0,
    fusion_scores=None,
):
    lines = []
    pulse_metrics = pulse_metrics or {}
    pulse_tags    = pulse_tags    or []
    fusion_scores = fusion_scores or {}

    lines.append("【结论性质】本结果基于PPG自动分析，仅反映当前时段脉搏特征倾向，不等同于临床确诊。")
    if fusion_primary:
        lines.append(f"【融合判定】{fusion_primary}（多特征融合）")
        lines.append(f"【区分度】主次得分差={fusion_gap}（越高表示判定越稳定）")
        if fusion_scores:
            lines.append(
                f"【融合得分】数={fusion_scores.get('数脉倾向', 0)}，"
                f"迟={fusion_scores.get('迟脉倾向', 0)}，"
                f"缓={fusion_scores.get('缓脉倾向', 0)}"
            )

    if fusion_primary == "数脉倾向":
        lines.append("【脉象倾向】数脉倾向（心率偏快）")
        lines.append("【解释】常见于紧张、运动后、发热等状态，需结合当时场景判读。")
    elif fusion_primary == "迟脉倾向":
        lines.append("【脉象倾向】迟脉倾向（心率偏慢）")
        lines.append("【解释】常见于静息、体能训练人群或个体差异，需结合基础心率判读。")
    else:
        lines.append("【脉象倾向】缓脉范围（心率中等）")

    if spo2 < 95:
        lines.append("【提示】血氧偏低，建议先排除体动、手指温度低、佩戴不稳等测量因素后复测。")

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


def evaluate_measurement_confidence(valid_rate, sample_count, duration_sec, pulse_metrics):
    score = 100
    reasons = []

    if duration_sec < MIN_MEASURE_SECONDS:
        score -= 35
        reasons.append(f"测量时长不足（{duration_sec}s<{MIN_MEASURE_SECONDS}s）")

    if sample_count < MIN_VALID_WINDOWS:
        score -= 30
        reasons.append(f"有效样本窗口不足（{sample_count}<{MIN_VALID_WINDOWS}）")

    if valid_rate < MIN_VALID_RATE:
        score -= 30
        reasons.append(f"有效窗口占比偏低（{valid_rate}%<{MIN_VALID_RATE}%）")

    signal_quality = pulse_metrics.get("signal_quality", 0.0)
    autocorr_ratio = pulse_metrics.get("autocorr_ratio", 0.0)
    if signal_quality < 0.85:
        score -= 10
        reasons.append(f"信号相关性一般（quality={signal_quality}）")
    if autocorr_ratio < 0.55:
        score -= 10
        reasons.append(f"周期性一般（autocorr={autocorr_ratio}）")

    score = max(0, min(100, score))
    if score >= 80:
        level = "high"
    elif score >= 60:
        level = "medium"
    else:
        level = "low"

    return {"score": score, "level": level, "reasons": reasons}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)