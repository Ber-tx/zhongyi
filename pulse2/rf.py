import serial
import json
import numpy as np
from scipy.stats import pearsonr
import time

# ===== RF算法常量（适配你的100Hz + 100样本）=====
FS = 100  # 采样率
BUFFER_SIZE = 100  # 缓冲区大小
mean_X = (BUFFER_SIZE - 1) / 2.0  # 49.5
x_indices = np.arange(BUFFER_SIZE) - mean_X
sum_X2 = np.sum(x_indices ** 2)  # 预计算：833250.0（精确值）

FS60 = FS * 60
LOWEST_PERIOD = int(FS60 / 180)  # 对应最高心率180bpm → 33
HIGHEST_PERIOD = int(FS60 / 40)  # 对应最低心率40bpm → 150

min_autocorrelation_ratio = 0.5  # 自相关比率阈值（越高越严，建议0.4~0.7）
min_pearson_correlation = 0.8  # Pearson阈值（越高越严，建议0.7~0.9）

# 全局变量：追踪上一次的峰值间隔（原版static变量，跨包保持稳定性）
last_peak_interval = LOWEST_PERIOD


# ===== RF算法核心函数 =====
def rf_calculate_hr_spo2(ir_buffer, red_buffer):
    global last_peak_interval

    ir = np.array(ir_buffer, dtype=float)
    red = np.array(red_buffer, dtype=float)

    # 1. 计算DC均值并去除DC
    ir_mean = np.mean(ir)
    red_mean = np.mean(red)
    ir_ac = ir - ir_mean
    red_ac = red - red_mean

    # 2. 线性去趋势（baseline leveling）
    beta_ir = np.sum(x_indices * ir_ac) / sum_X2
    beta_red = np.sum(x_indices * red_ac) / sum_X2
    ir_ac -= beta_ir * x_indices
    red_ac -= beta_red * x_indices

    # 3. 计算AC RMS 和 平方和（用于相关性）
    ir_sumsq = np.sum(ir_ac ** 2)
    red_sumsq = np.sum(red_ac ** 2)
    ir_rms = np.sqrt(ir_sumsq / BUFFER_SIZE)
    red_rms = np.sqrt(red_sumsq / BUFFER_SIZE)

    # 4. Pearson相关系数
    if ir_sumsq == 0 or red_sumsq == 0:
        correl = 0.0
    else:
        correl = pearsonr(ir_ac, red_ac)[0]  # 只取系数

    # 5. 自相关周期性检测
    ratio = 0.0
    if correl >= min_pearson_correlation:
        # 计算lag=0的自相关（能量）
        aut_lag0 = ir_sumsq / BUFFER_SIZE

        # 初始化搜索（仅第一次或丢失时）
        if last_peak_interval == LOWEST_PERIOD:
            initialize_periodicity_search(ir_ac, aut_lag0)

        # 正常周期性搜索
        if last_peak_interval != 0:
            signal_periodicity(ir_ac, aut_lag0, ratio_out=[ratio])

    # 6. 心率计算
    if last_peak_interval != 0 and LOWEST_PERIOD <= last_peak_interval <= HIGHEST_PERIOD:
        hr = FS60 / last_peak_interval
        hr_valid = True
    else:
        hr = None
        hr_valid = False
        last_peak_interval = LOWEST_PERIOD  # 重置

    # 7. SpO2计算
    spo2 = None
    spo2_valid = False
    if hr_valid and ir_rms > 0 and red_rms > 0:
        xy_ratio = (red_rms * ir_mean) / (ir_rms * red_mean)
        if 0.02 < xy_ratio < 1.84:  # 有效范围
            spo2 = (-45.060 * xy_ratio + 30.354) * xy_ratio + 94.845
            spo2 = np.clip(spo2, 0, 100)
            spo2_valid = True

    return {
        "hr": round(hr, 1) if hr else None,
        "spo2": round(spo2, 1) if spo2 else None,
        "hr_valid": hr_valid,
        "spo2_valid": spo2_valid and correl >= min_pearson_correlation,
        "autocorr_ratio": round(ratio, 3),
        "pearson_corr": round(correl, 3),
        "xy_ratio": round((red_rms * ir_mean) / (ir_rms * red_mean), 3) if ir_rms > 0 and red_rms > 0 else None
    }


# 辅助：初始化周期搜索
def initialize_periodicity_search(ir_ac, aut_lag0):
    global last_peak_interval
    n_lag = last_peak_interval
    aut = rf_autocorrelation(ir_ac, n_lag)
    aut_right = aut
    while (aut_right / aut_lag0 >= min_autocorrelation_ratio and
           aut_right < aut and n_lag <= HIGHEST_PERIOD):
        aut = aut_right
        n_lag += 2
        aut_right = rf_autocorrelation(ir_ac, n_lag)
    while (aut_right / aut_lag0 < min_autocorrelation_ratio and n_lag <= HIGHEST_PERIOD):
        aut = aut_right
        n_lag += 2
        aut_right = rf_autocorrelation(ir_ac, n_lag)
    if n_lag > HIGHEST_PERIOD:
        last_peak_interval = 0
    else:
        last_peak_interval = n_lag


# 辅助：正常周期性搜索
def signal_periodicity(ir_ac, aut_lag0, ratio_out):
    global last_peak_interval
    n_lag = last_peak_interval
    aut = rf_autocorrelation(ir_ac, n_lag)
    aut_left = aut
    left_limit = False

    # 向左搜索更高峰
    while aut_left > aut and n_lag >= LOWEST_PERIOD:
        aut = aut_left
        n_lag -= 1
        aut_left = rf_autocorrelation(ir_ac, n_lag)
    if n_lag < LOWEST_PERIOD:
        left_limit = True
        n_lag = last_peak_interval
        aut = rf_autocorrelation(ir_ac, n_lag)
    else:
        n_lag += 1

    # 如果左边没进步，向右搜索
    if n_lag == last_peak_interval:
        aut_right = aut
        while aut_right > aut and n_lag <= HIGHEST_PERIOD:
            aut = aut_right
            n_lag += 1
            aut_right = rf_autocorrelation(ir_ac, n_lag)
        n_lag -= 1
        if n_lag > HIGHEST_PERIOD or (n_lag == last_peak_interval and left_limit):
            last_peak_interval = 0
            ratio_out[0] = 0.0
            return

    # 计算当前比率
    ratio_out[0] = aut / aut_lag0 if aut_lag0 > 0 else 0.0
    last_peak_interval = n_lag


# 辅助：自相关计算
def rf_autocorrelation(ac_signal, lag):
    if lag == 0:
        return np.sum(ac_signal ** 2) / BUFFER_SIZE
    n_temp = BUFFER_SIZE - lag
    if n_temp <= 0:
        return 0.0
    return np.sum(ac_signal[:n_temp] * ac_signal[lag:lag + n_temp]) / n_temp


# ===== 串口接收主循环 =====
SERIAL_PORT = 'COM7'  # 修改为你的实际端口（Windows: COMx, Linux/Mac: /dev/ttyUSBx 或 /dev/ttyACM0）
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
print(f"正在连接 {SERIAL_PORT} @ {BAUD_RATE}...")

while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith('{"ir":'):
            data = json.loads(line)
            ir_buffer = data['ir']
            red_buffer = data['red']

            if len(ir_buffer) == BUFFER_SIZE and len(red_buffer) == BUFFER_SIZE:
                result = rf_calculate_hr_spo2(ir_buffer, red_buffer)

                timestamp = data.get('timestamp', time.time())
                print(f"\n[{time.strftime('%H:%M:%S')}] 时间戳: {timestamp}")
                print(f"心率: {result['hr']} bpm {'(有效)' if result['hr_valid'] else '(无效)'}")
                print(f"血氧: {result['spo2']}% {'(有效)' if result['spo2_valid'] else '(无效)'}")
                print(
                    f"质量指标 → 自相关比率: {result['autocorr_ratio']}, Pearson: {result['pearson_corr']}, XY比率: {result['xy_ratio']}")
            else:
                print("警告: 数据包长度不对，忽略")
    except Exception as e:
        print(f"错误: {e}")
        time.sleep(0.1)