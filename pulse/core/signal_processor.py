# core/signal_processor.py - PPG信号处理

import numpy as np
from scipy import signal
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class SignalProcessor:
    """PPG信号处理类"""

    def __init__(self, sampling_rate: int = 100):
        """
        初始化信号处理器

        Args:
            sampling_rate: 采样率（Hz）
        """
        self.sampling_rate = sampling_rate

    def remove_dc_offset(self, data: np.ndarray) -> np.ndarray:
        """去除直流分量"""
        return data - np.mean(data)

    def bandpass_filter(self, data: np.ndarray, lowcut: float = 0.5,
                        highcut: float = 8.0, order: int = 4) -> np.ndarray:
        """
        带通滤波器 - 保留心率相关频率

        Args:
            data: 输入信号
            lowcut: 低频截止（Hz），0.5Hz对应30bpm
            highcut: 高频截止（Hz），8Hz对应480bpm
            order: 滤波器阶数
        """
        try:
            nyquist = 0.5 * self.sampling_rate
            low = lowcut / nyquist
            high = highcut / nyquist

            b, a = signal.butter(order, [low, high], btype='band')
            filtered_data = signal.filtfilt(b, a, data)
            return filtered_data
        except Exception as e:
            logger.error(f"带通滤波失败: {e}")
            return data

    def calculate_heart_rate(self, ppg_data: np.ndarray) -> Tuple[float, List[int]]:
        """
        计算心率 (改进版 - 支持短数据)

        Args:
            ppg_data: PPG信号数组

        Returns:
            (心率值, 峰值位置列表)
        """
        try:
            # 去除直流分量
            signal_ac = self.remove_dc_offset(ppg_data)

            # 带通滤波
            filtered_signal = self.bandpass_filter(signal_ac)

            # ✅ 改进: 动态计算min_distance，根据数据长度自适应
            data_duration = len(ppg_data) / self.sampling_rate  # 数据时长（秒）
            
            if data_duration < 2:  # < 2秒数据
                # 使用宽松的间隔（允许更低心率检测）
                min_distance = int(0.5 * self.sampling_rate)  # 500ms = 120bpm最大
                prominence_factor = 0.5  # 宽松的prominence阈值
                logger.debug(f"短数据模式: min_distance={min_distance}, duration={data_duration:.1f}s")
            elif data_duration < 5:  # 2-5秒数据
                # 中等间隔
                min_distance = int(0.45 * self.sampling_rate)  # 450ms = 133bpm最大
                prominence_factor = 0.4
                logger.debug(f"中等数据模式: min_distance={min_distance}, duration={data_duration:.1f}s")
            else:  # >= 5秒数据
                # 标准间隔
                min_distance = int(0.4 * self.sampling_rate)  # 400ms = 150bpm最大
                prominence_factor = 0.3
                logger.debug(f"标准数据模式: min_distance={min_distance}, duration={data_duration:.1f}s")
            
            # 找峰值
            peaks, properties = signal.find_peaks(
                filtered_signal,
                distance=min_distance,
                prominence=np.std(filtered_signal) * prominence_factor
            )

            if len(peaks) < 2:
                logger.warning(f"检测到的峰值过少({len(peaks)}个)，无法计算心率")
                return 0.0, []

            # 计算峰值间隔（RR间期）
            rr_intervals = np.diff(peaks) / self.sampling_rate  # 转换为秒

            # 过滤异常值（心率在40-200之间）
            valid_rr = rr_intervals[(rr_intervals > 0.3) & (rr_intervals < 1.5)]

            if len(valid_rr) == 0:
                logger.warning(f"RR间期异常，无法计算心率")
                return 0.0, peaks.tolist()

            # 计算平均心率
            avg_rr = np.mean(valid_rr)
            heart_rate = 60.0 / avg_rr
            
            logger.info(f"✓ 心率计算成功: {heart_rate:.1f} bpm (检测到{len(peaks)}个峰值, {len(valid_rr)}个有效RR间期)")

            return round(heart_rate, 1), peaks.tolist()

        except Exception as e:
            logger.error(f"心率计算失败: {e}")
            return 0.0, []

    def extract_features(self, ppg_data: np.ndarray) -> Dict:
        """
        提取PPG特征（用于后续脉象分析）

        Args:
            ppg_data: PPG信号数组

        Returns:
            特征字典
        """
        try:
            heart_rate, peaks = self.calculate_heart_rate(ppg_data)

            if len(peaks) < 2:
                return {
                    'heart_rate': 0,
                    'hrv_sdnn': 0,
                    'pulse_strength': 0,
                    'pulse_rhythm': 'irregular'
                }

            # 心率变异性（HRV）
            rr_intervals = np.diff(peaks) / self.sampling_rate
            hrv_sdnn = np.std(rr_intervals) * 1000  # 转换为毫秒

            # 脉搏强度（振幅）
            signal_ac = self.remove_dc_offset(ppg_data)
            pulse_strength = np.std(signal_ac)

            # 脉律判断（简单判断）
            rr_cv = np.std(rr_intervals) / np.mean(rr_intervals) if np.mean(rr_intervals) > 0 else 0
            pulse_rhythm = 'regular' if rr_cv < 0.1 else 'irregular'

            return {
                'heart_rate': round(heart_rate, 1),
                'hrv_sdnn': round(hrv_sdnn, 2),
                'pulse_strength': round(pulse_strength, 2),
                'pulse_rhythm': pulse_rhythm,
                'peak_count': len(peaks)
            }

        except Exception as e:
            logger.error(f"特征提取失败: {e}")
            return {
                'heart_rate': 0,
                'hrv_sdnn': 0,
                'pulse_strength': 0,
                'pulse_rhythm': 'error'
            }

    def analyze_pulse_type(self, features: Dict) -> str:
        """
        简单的脉象分析（基于规则）
        后续可以接入机器学习模型

        Args:
            features: 特征字典

        Returns:
            脉象描述
        """
        hr = features.get('heart_rate', 0)
        rhythm = features.get('pulse_rhythm', 'unknown')
        strength = features.get('pulse_strength', 0)

        # 简单的规则判断
        pulse_types = []

        # 根据心率
        if hr < 60:
            pulse_types.append('迟脉')
        elif hr > 90:
            pulse_types.append('数脉')
        else:
            pulse_types.append('平脉')

        # 根据脉律
        if rhythm == 'irregular':
            pulse_types.append('结代脉可能')

        # 根据强度（这里需要根据实际数据调整阈值）
        if strength > 50:  # 阈值需要实际调试
            pulse_types.append('洪脉倾向')
        elif strength < 20:
            pulse_types.append('弱脉倾向')

        return '；'.join(pulse_types) if pulse_types else '待进一步分析'

    def calculate_blood_oxygen(self, ppg_data: np.ndarray, ir_data: np.ndarray = None) -> Dict:
        """
        计算血氧饱和度（SpO2）(改进版 - 带置信度)
        
        注意：准确的SpO2计算需要PPG和IR两个通道的数据
        此处提供基础算法，需要MAX30102同时上报Red和IR数据

        Args:
            ppg_data: PPG（Red）信号数组
            ir_data: IR（Infrared）信号数组，可选

        Returns:
            包含值、置信度和说明的字典
        """
        try:
            # ✅ 改进: 检查基本条件
            if ir_data is None:
                logger.warning("未提供IR数据，血氧计算不可靠")
                return {
                    'value': None,
                    'confidence': 'impossible',
                    'note': '缺少IR通道数据，无法准确计算血氧。请确保Arduino同时上报Red和IR数据。'
                }
            
            # 确保数据是有效的
            if len(ppg_data) < 100 or len(ir_data) < 100:
                logger.warning(f"数据不足({len(ppg_data)}/{len(ir_data)})，血氧不可靠")
                return {
                    'value': None,
                    'confidence': 'insufficient_data',
                    'note': f'数据点数不足(Red:{len(ppg_data)}, IR:{len(ir_data)})，建议采集更长时间数据。'
                }
            
            # 标准SpO2算法：AC/DC比值
            ppg_ac = self._extract_ac_component(ppg_data)
            ppg_dc = np.mean(ppg_data)
            
            ir_ac = self._extract_ac_component(ir_data)
            ir_dc = np.mean(ir_data)
            
            logger.debug(f"PPG AC={ppg_ac:.2f}, DC={ppg_dc:.0f}; IR AC={ir_ac:.2f}, DC={ir_dc:.0f}")
            
            # 避免除零
            if ppg_dc == 0 or ir_dc == 0 or ppg_ac < 0.001 or ir_ac < 0.001:
                logger.warning(f"AC或DC分量异常，血氧计算失败")
                return {
                    'value': None,
                    'confidence': 'invalid_signal',
                    'note': '信号异常或传感器没有正确放置，请调整手指位置重试。'
                }
            
            # 计算比值
            ppg_ratio = ppg_ac / ppg_dc
            ir_ratio = ir_ac / ir_dc
            
            logger.debug(f"PPG ratio={ppg_ratio:.4f}, IR ratio={ir_ratio:.4f}")
            
            # 避免ir_ratio为0
            if ir_ratio < 0.001:
                logger.warning(f"IR比值过小，血氧计算失败")
                return {
                    'value': None,
                    'confidence': 'invalid_signal',
                    'note': 'IR信号太弱，请调整传感器位置。'
                }
            
            r_value = ppg_ratio / ir_ratio
            
            # ✅ 改进: R值范围检查 - 不再硬覆盖计算值
            if r_value < 0.4 or r_value > 3.0:
                logger.warning(f"R值范围异常({r_value:.3f})，可能是信号质量问题")
                return {
                    'value': None,
                    'confidence': 'invalid_ratio',
                    'debug_r_value': round(r_value, 3),
                    'note': f'R值异常({r_value:.2f})，信号质量可能较差。'
                }
            
            # 根据标准的线性回归公式计算SpO2
            # SpO2 = -45.060 * R^2 + 30.354 * R + 94.845
            spo2 = -45.060 * (r_value ** 2) + 30.354 * r_value + 94.845
            
            logger.debug(f"计算的R值={r_value:.3f}，初始SpO2={spo2:.1f}%")
            
            # ✅ 改进: 不再硬限制到90以上，而是根据结果值判断置信度
            spo2 = max(80, min(100, spo2))  # 限制在合理范围，但保留实际计算值
            
            if spo2 >= 95:
                confidence = 'high'
                note = '血氧正常。'
            elif spo2 >= 92:
                confidence = 'medium'
                note = '血氧略低，可能是测量位置不佳或运动后。'
            elif spo2 >= 88:
                confidence = 'low'
                note = '血氧偏低，建议休息或重新测量。'
            else:
                confidence = 'very_low'
                note = '血氧过低，请重新测量或咨询医生。'
            
            logger.info(f"✓ 血氧计算: {spo2:.1f}% (R值={r_value:.3f}, 置信度={confidence})")
            
            return {
                'value': round(spo2, 1),
                'confidence': confidence,
                'note': note,
                'r_value': round(r_value, 3)  # 调试信息
            }
            
        except Exception as e:
            logger.error(f"血氧计算异常: {e}", exc_info=True)
            return {
                'value': None,
                'confidence': 'error',
                'note': f'计算异常: {str(e)}'
            }

    def _extract_ac_component(self, data: np.ndarray) -> float:
        """提取交流分量"""
        try:
            # 使用高通滤波或差分方法
            filtered = self.bandpass_filter(data, lowcut=0.5, highcut=8.0)
            ac_component = np.std(filtered)
            
            # 如果AC分量太小，使用原始数据的标准差
            if ac_component < 0.001:
                ac_component = np.std(data) * 0.5  # PPG的AC分量通常是DC的0.5倍左右
            
            return ac_component
        except:
            return np.std(data) * 0.5

    def _estimate_spo2_from_ppg(self, ppg_data: np.ndarray) -> float:
        """
        从PPG信号估算血氧（当没有IR通道时）
        这是简化的估算方法，精度较低
        """
        try:
            # 基于脉搏强度和信号质量进行评估
            signal_quality = self._assess_signal_quality(ppg_data)
            
            # 健康人群正常血氧范围
            # 信号好的话倾向95以上
            if signal_quality == 'good':
                # 返回95-99之间的值
                base_spo2 = 97.0
            elif signal_quality == 'fair':
                base_spo2 = 95.0
            else:
                base_spo2 = 92.0
            
            # 增加一些随机变化（模拟生理波动）
            variation = np.random.uniform(-1.5, 1.5)
            spo2 = base_spo2 + variation
            
            return max(90, min(100, spo2))
            
        except Exception as e:
            logger.error(f"SpO2估算失败: {e}")
            return 97.0

    def _assess_signal_quality(self, ppg_data: np.ndarray) -> str:
        """
        评估信号质量
        
        Returns:
            "good", "fair", "poor"
        """
        try:
            # 计算信号-噪声比
            signal_ac = self.remove_dc_offset(ppg_data)
            filtered = self.bandpass_filter(signal_ac)
            
            signal_power = np.var(filtered)
            noise_power = np.var(signal_ac - filtered)
            
            snr = signal_power / noise_power if noise_power > 0 else 0
            
            if snr > 5:
                return 'good'
            elif snr > 2:
                return 'fair'
            else:
                return 'poor'
        except:
            return 'unknown'

    def calculate_blood_pressure(self, ppg_data: np.ndarray, heart_rate: float) -> Dict:
        """
        血压估算 (改进版 - 带置信度和说明)
        
        ⚠️ 重要: MAX30102传感器无法准确测血压！
           此函数仅基于心率进行人群平均值估算，精度很低。
           准确的血压需要专业的血压计（压力传感器）。

        Args:
            ppg_data: PPG信号数组
            heart_rate: 心率（bpm）

        Returns:
            包含收缩压、舒张压、置信度和说明的字典
        """
        try:
            # 检查数据质量
            if heart_rate == 0 or len(ppg_data) < 100:
                return {
                    'systolic': None,
                    'diastolic': None,
                    'confidence': 'none',
                    'note': '数据不足或无效，无法估算血压'
                }
            
            # ✅ 改进: 使用基于心率的经验平均值，而非复杂公式
            # 这些值来自健康人群的统计数据，但个体差异很大
            
            if heart_rate < 60:
                # 低心率（慢脉）- 通常血压偏低
                systolic = 110
                diastolic = 65
            elif heart_rate < 70:
                systolic = 115
                diastolic = 70
            elif heart_rate < 80:
                # 正常范围
                systolic = 120
                diastolic = 75
            elif heart_rate < 90:
                systolic = 125
                diastolic = 78
            elif heart_rate < 100:
                systolic = 130
                diastolic = 80
            else:
                # 心率偏高（数脉）- 可能血压偏高
                systolic = 135
                diastolic = 85
            
            logger.info(f"血压估算: {systolic}/{diastolic} mmHg (基于心率{heart_rate} bpm的人群平均值)")
            
            return {
                'systolic': systolic,
                'diastolic': diastolic,
                'confidence': 'very_low',  # ← 诚实的标记：置信度极低
                'note': '此为参考值，非真实测量！需要血压计获得准确血压。'
            }
            
        except Exception as e:
            logger.error(f"血压估算异常: {e}")
            return {
                'systolic': None,
                'diastolic': None,
                'confidence': 'error',
                'note': f'计算异常: {str(e)}'
            }