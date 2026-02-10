import numpy as np
from scipy.stats import pearsonr


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

        # ===== 状态变量 (替代原代码中的 global) =====
        self.last_peak_interval = self.LOWEST_PERIOD

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
        """ 对应原 rf_calculate_hr_spo2 函数 """
        ir = np.array(ir_buffer, dtype=float)
        red = np.array(red_buffer, dtype=float)

        # 1. 计算DC均值并去除DC
        ir_mean = np.mean(ir)
        red_mean = np.mean(red)
        ir_ac = ir - ir_mean
        red_ac = red - red_mean

        # 2. 线性去趋势（baseline leveling）
        beta_ir = np.sum(self.x_indices * ir_ac) / self.sum_X2
        beta_red = np.sum(self.x_indices * red_ac) / self.sum_X2
        ir_ac -= beta_ir * self.x_indices
        red_ac -= beta_red * self.x_indices

        # 3. 计算AC RMS 和 平方和
        ir_sumsq = np.sum(ir_ac ** 2)
        red_sumsq = np.sum(red_ac ** 2)
        ir_rms = np.sqrt(ir_sumsq / self.BUFFER_SIZE)
        red_rms = np.sqrt(red_sumsq / self.BUFFER_SIZE)

        # 4. Pearson相关系数
        if ir_sumsq == 0 or red_sumsq == 0:
            correl = 0.0
        else:
            correl = pearsonr(ir_ac, red_ac)[0]

        # 5. 自相关周期性检测
        ratio = 0.0
        if correl >= self.min_pearson_correlation:
            aut_lag0 = ir_sumsq / self.BUFFER_SIZE

            # 初始化搜索
            if self.last_peak_interval == self.LOWEST_PERIOD:
                self.initialize_periodicity_search(ir_ac, aut_lag0)

            # 正常搜索
            if self.last_peak_interval != 0:
                ratio_list = [ratio]  # 传递列表以实现引用修改
                self.signal_periodicity(ir_ac, aut_lag0, ratio_list)
                ratio = ratio_list[0]

        # 6. 心率计算
        hr = None
        hr_valid = False
        if self.last_peak_interval != 0 and self.LOWEST_PERIOD <= self.last_peak_interval <= self.HIGHEST_PERIOD:
            hr = self.FS60 / self.last_peak_interval
            hr_valid = True
        else:
            self.last_peak_interval = self.LOWEST_PERIOD  # 重置

        # 7. SpO2计算
        spo2 = None
        spo2_valid = False
        xy_ratio = 0.0

        if hr_valid and ir_rms > 0 and red_rms > 0:
            xy_ratio = (red_rms * ir_mean) / (ir_rms * red_mean)
            if 0.02 < xy_ratio < 1.84:
                spo2 = (-45.060 * xy_ratio + 30.354) * xy_ratio + 94.845
                spo2 = np.clip(spo2, 0, 100)
                spo2_valid = True

        # 返回结果字典
        return {
            "hr": round(float(hr), 1) if hr else 0.0,
            "spo2": round(float(spo2), 1) if spo2 else 0.0,
            "hr_valid": bool(hr_valid),
            "spo2_valid": bool(spo2_valid and correl >= self.min_pearson_correlation),
            "quality": round(float(correl), 3),
            "is_valid": bool(hr_valid and (correl >= self.min_pearson_correlation))
        }

    def reset(self):
        """重置算法状态（供新测量开始时调用）"""
        self.last_peak_interval = self.LOWEST_PERIOD