import numpy as np
from scipy.stats import pearsonr
from scipy import signal


class PulseAlgorithm:
    def __init__(self, buffer_size=50, fs=50):
        # ===== 常量定义 =====
        self.FS = fs
        self.BUFFER_SIZE = buffer_size
        self.mean_X = (self.BUFFER_SIZE - 1) / 2.0
        self.x_indices = np.arange(self.BUFFER_SIZE) - self.mean_X
        self.sum_X2 = np.sum(self.x_indices ** 2)

        self.FS60 = self.FS * 60
        self.LOWEST_PERIOD = int(self.FS60 / 180)  # 33
        self.HIGHEST_PERIOD = int(self.FS60 / 40)  # 150

        self.min_autocorrelation_ratio = 0.5
        self.min_pearson_correlation = 0.8

        # ===== 状态变量 (替代 global) =====
        self.last_peak_interval = self.LOWEST_PERIOD
        self._bandpass_sos = signal.butter(
            3,
            [0.7 / (self.FS / 2.0), 3.5 / (self.FS / 2.0)],
            btype="bandpass",
            output="sos",
        )

    def _bandpass(self, x):
        """PPG 生理频段滤波：0.7~3.5Hz 对应约 42~210bpm。"""
        if len(x) < 10:
            return np.asarray(x, dtype=float)
        return signal.sosfiltfilt(self._bandpass_sos, np.asarray(x, dtype=float))

    def _autocorr_ratio(self, x, lag):
        if len(x) <= lag or lag <= 0:
            return 0.0
        x = np.asarray(x, dtype=float)
        e0 = np.sum(x * x)
        if e0 <= 1e-9:
            return 0.0
        e1 = np.sum(x[:-lag] * x[lag:])
        return float(max(0.0, e1 / e0))

    def rf_autocorrelation(self, ac_signal, lag):
        """ 辅助：自相关计算 """
        if lag == 0:
            return np.sum(ac_signal ** 2) / self.BUFFER_SIZE
        n_temp = self.BUFFER_SIZE - lag
        if n_temp <= 0:
            return 0.0
        return np.sum(ac_signal[:n_temp] * ac_signal[lag:lag + n_temp]) / n_temp

    def initialize_periodicity_search(self, ir_ac, aut_lag0):
        """ 辅助：初始化周期搜索 """
        n_lag = self.last_peak_interval
        aut = self.rf_autocorrelation(ir_ac, n_lag)
        aut_right = aut

        # 向右搜索
        while (aut_right / aut_lag0 >= self.min_autocorrelation_ratio and
               aut_right < aut and n_lag <= self.HIGHEST_PERIOD):
            aut = aut_right
            n_lag += 2
            aut_right = self.rf_autocorrelation(ir_ac, n_lag)

        while (aut_right / aut_lag0 < self.min_autocorrelation_ratio and n_lag <= self.HIGHEST_PERIOD):
            aut = aut_right
            n_lag += 2
            aut_right = self.rf_autocorrelation(ir_ac, n_lag)

        if n_lag > self.HIGHEST_PERIOD:
            self.last_peak_interval = 0
        else:
            self.last_peak_interval = n_lag

    def signal_periodicity(self, ir_ac, aut_lag0, ratio_out):
        """ 辅助：正常周期性搜索 """
        n_lag = self.last_peak_interval
        aut = self.rf_autocorrelation(ir_ac, n_lag)
        aut_left = aut
        left_limit = False

        # 向左搜索更高峰
        while aut_left > aut and n_lag >= self.LOWEST_PERIOD:
            aut = aut_left
            n_lag -= 1
            aut_left = self.rf_autocorrelation(ir_ac, n_lag)

        if n_lag < self.LOWEST_PERIOD:
            left_limit = True
            n_lag = self.last_peak_interval
            aut = self.rf_autocorrelation(ir_ac, n_lag)
        else:
            n_lag += 1

        # 如果左边没进步，向右搜索
        if n_lag == self.last_peak_interval:
            aut_right = aut
            while aut_right > aut and n_lag <= self.HIGHEST_PERIOD:
                aut = aut_right
                n_lag += 1
                aut_right = self.rf_autocorrelation(ir_ac, n_lag)
            n_lag -= 1

        if n_lag > self.HIGHEST_PERIOD or (n_lag == self.last_peak_interval and left_limit):
            self.last_peak_interval = 0
            ratio_out[0] = 0.0
            return

        # 计算当前比率
        ratio_out[0] = aut / aut_lag0 if aut_lag0 > 0 else 0.0
        self.last_peak_interval = n_lag

    def process(self, ir_buffer, red_buffer):
        """
        对应原 rf_calculate_hr_spo2 函数
        在保持接口不变前提下，改为更稳健的 HR/SpO2 计算流程：
        1) 带通滤波抑制漂移与高频噪声
        2) 时域峰值+频域主频双通道融合心率
        3) 基于质量门控的 ratio-of-ratios 血氧估计
        """
        ir = np.asarray(ir_buffer, dtype=float)
        red = np.asarray(red_buffer, dtype=float)

        if len(ir) != len(red) or len(ir) < max(32, int(1.5 * self.FS)):
            return {
                "hr": 0.0,
                "spo2": 0.0,
                "hr_valid": False,
                "spo2_valid": False,
                "quality": 0.0,
                "is_valid": False,
                "autocorr_ratio": 0.0,
                "pearson_corr": 0.0,
                "xy_ratio": 0.0,
                "ir_rms": 0.0,
                "red_rms": 0.0,
                "ir_mean": 0.0,
                "red_mean": 0.0,
            }

        # 1) DC 与 AC 分离
        ir_mean = float(np.mean(ir))
        red_mean = float(np.mean(red))
        ir_ac = ir - ir_mean
        red_ac = red - red_mean

        # 2) 去趋势 + 生理频段带通
        ir_detrend = signal.detrend(ir_ac, type="linear")
        red_detrend = signal.detrend(red_ac, type="linear")
        ir_bp = self._bandpass(ir_detrend)
        red_bp = self._bandpass(red_detrend)

        # 3) 计算 AC RMS、相关性
        ir_rms = float(np.sqrt(np.mean(ir_bp ** 2)))
        red_rms = float(np.sqrt(np.mean(red_bp ** 2)))
        if ir_rms <= 1e-9 or red_rms <= 1e-9:
            correl = 0.0
        else:
            correl = float(pearsonr(ir_bp, red_bp)[0])
            if np.isnan(correl):
                correl = 0.0

        # 4) 时域心率：峰间距
        min_distance = max(1, int(self.FS * 60.0 / 180.0))
        prom = max(1e-9, 0.45 * float(np.std(ir_bp)))
        peaks, _ = signal.find_peaks(ir_bp, distance=min_distance, prominence=prom)

        hr_time = 0.0
        hr_time_valid = False
        if len(peaks) >= 3:
            rr = np.diff(peaks).astype(float)
            rr = rr[(rr >= self.LOWEST_PERIOD) & (rr <= self.HIGHEST_PERIOD)]
            if len(rr) >= 2:
                period = float(np.median(rr))
                if period > 0:
                    hr_time = self.FS60 / period
                    hr_time_valid = 40.0 <= hr_time <= 180.0

        # 5) 频域心率：主频峰
        f, pxx = signal.welch(ir_bp, fs=self.FS, nperseg=min(len(ir_bp), 128))
        band = (f >= 40.0 / 60.0) & (f <= 180.0 / 60.0)
        hr_freq = 0.0
        hr_freq_valid = False
        if np.any(band):
            fb = f[band]
            pb = pxx[band]
            if len(pb) > 0 and np.max(pb) > 0:
                dom_f = float(fb[int(np.argmax(pb))])
                hr_freq = dom_f * 60.0
                hr_freq_valid = 40.0 <= hr_freq <= 180.0

        # 6) 融合心率
        hr = 0.0
        hr_valid = False
        if hr_time_valid and hr_freq_valid:
            delta = abs(hr_time - hr_freq)
            if delta <= 8.0:
                hr = 0.65 * hr_time + 0.35 * hr_freq
                hr_valid = True
            else:
                # 双通道冲突时，优先时域（对 PPG 更直观）
                hr = hr_time
                hr_valid = correl >= 0.60
        elif hr_time_valid:
            hr = hr_time
            hr_valid = correl >= 0.60
        elif hr_freq_valid:
            hr = hr_freq
            hr_valid = correl >= 0.70

        # 7) 周期性指标（供上层做质量过滤）
        ratio = 0.0
        if hr_valid and hr > 0:
            lag = int(round(self.FS60 / hr))
            ratio = self._autocorr_ratio(ir_bp, lag)

        # 8) 血氧估计：ratio-of-ratios + 严格质量门控
        spo2 = 0.0
        spo2_valid = False
        xy_ratio = 0.0
        if hr_valid and ir_mean > 1e-6 and red_mean > 1e-6 and ir_rms > 1e-9 and red_rms > 1e-9:
            ir_ac_dc = ir_rms / (ir_mean + 1e-12)
            red_ac_dc = red_rms / (red_mean + 1e-12)
            xy_ratio = red_ac_dc / (ir_ac_dc + 1e-12)

            # 常见经验式：SpO2 = 110 - 25R，更稳健，便于后期标定
            spo2_est = 110.0 - 25.0 * xy_ratio
            spo2_est = float(np.clip(spo2_est, 70.0, 100.0))

            # 质量门控：相关性、周期性、R值合理范围
            if correl >= 0.60 and ratio >= 0.35 and 0.2 <= xy_ratio <= 1.4:
                spo2 = spo2_est
                spo2_valid = True

        quality = float(np.clip(0.75 * max(0.0, correl) + 0.25 * np.clip(ratio, 0.0, 1.0), 0.0, 1.0))
        is_valid = bool(hr_valid and quality >= 0.45)

        # 返回结果字典
        return {
            "hr": round(float(hr), 1) if hr_valid else 0.0,
            "spo2": round(float(spo2), 1) if spo2_valid else 0.0,
            "hr_valid": bool(hr_valid),
            "spo2_valid": bool(spo2_valid),
            "quality": round(float(quality), 3),
            "is_valid": is_valid,
            "autocorr_ratio": round(float(ratio), 3),
            "pearson_corr": round(float(correl), 3),
            "xy_ratio": round(float(xy_ratio), 3) if xy_ratio else 0.0,
            "ir_rms": round(float(ir_rms), 6),
            "red_rms": round(float(red_rms), 6),
            "ir_mean": round(float(ir_mean), 6),
            "red_mean": round(float(red_mean), 6)
        }

    def reset(self):
        """重置算法状态（供新测量开始时调用）"""
        self.last_peak_interval = self.LOWEST_PERIOD