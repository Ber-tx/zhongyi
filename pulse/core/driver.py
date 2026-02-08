# core/driver.py - 脉诊数据处理驱动

import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from .signal_processor import SignalProcessor
from .data_models import (
    PulseAnalysisResult, ExtendedPulseData, WaveformData,
    BloodPressure, APIResponse
)
from config import config

logger = logging.getLogger(__name__)


class PulseDataProcessor:
    """脉诊数据处理器"""

    def __init__(self):
        """初始化处理器"""
        self.signal_processor = SignalProcessor(sampling_rate=config.SAMPLING_RATE)
        logger.info("脉诊数据处理器初始化完成")

    def process_raw_data(self, raw_data: Dict[str, Any], mode: str = 'simple') -> Dict[str, Any]:
        """
        处理ESP32发来的原始数据

        Args:
            raw_data: 原始数据字典，格式如下：
            {
                "ppg": [123, 456, 789, ...],  # PPG信号数组
                "ir": [234, 567, 890, ...],    # 红外信号（可选）
                "timestamp": "2024-01-01 12:00:00",
                "user_id": 1
            }
            mode: 处理模式
                - 'simple': 简化模式（5个字段，用于前端展示）
                - 'extended': 扩展模式（包含详细分析，用于数据库保存）

        Returns:
            根据mode返回不同格式的数据字典
        """
        try:
            logger.info(f"开始处理原始数据，用户ID: {raw_data.get('user_id', 'unknown')}, 模式: {mode}")

            # 提取PPG数据
            ppg_data = raw_data.get('ppg', [])

            if not ppg_data or len(ppg_data) < 100:
                logger.warning(f"PPG数据不足: {len(ppg_data)} 个采样点")
                return self._create_error_response("数据量不足", mode)

            # 转换为numpy数组
            ppg_array = np.array(ppg_data, dtype=np.float64)

            # 数据验证
            if not self._validate_signal(ppg_array):
                logger.warning("信号质量不佳")
                return self._create_error_response("信号质量不佳", mode)

            # 提取特征
            features = self.signal_processor.extract_features(ppg_array)
            
            if features['heart_rate'] == 0:
                return self._create_error_response("无法计算心率", mode)

            # 根据模式返回不同格式的数据
            if mode == 'simple':
                return self._process_simple_mode(raw_data, ppg_array, features)
            else:
                return self._process_extended_mode(raw_data, ppg_array, features)

        except Exception as e:
            logger.error(f"数据处理失败: {e}", exc_info=True)
            return self._create_error_response(f"处理异常: {str(e)}", mode)

    def _process_simple_mode(self, raw_data: Dict, ppg_array: np.ndarray, features: Dict) -> Dict:
        """
        简化模式处理 - 返回5个核心字段（包含置信度和说明）
        
        用于：前端实时展示、API响应
        """
        try:
            heart_rate = features['heart_rate']
            
            # 计算血氧（现在返回Dict）
            ir_data = raw_data.get('ir')
            if ir_data:
                ir_array = np.array(ir_data, dtype=np.float64)
            else:
                ir_array = None
            blood_oxygen_result = self.signal_processor.calculate_blood_oxygen(ppg_array, ir_array)
            
            # 计算血压（现在返回Dict，包含置信度）
            blood_pressure_result = self.signal_processor.calculate_blood_pressure(ppg_array, heart_rate)
            
            # 脉象分析
            pulse_type = self.signal_processor.analyze_pulse_type(features)
            
            # 创建简化结果
            result = PulseAnalysisResult(
                heart_rate=heart_rate,
                blood_oxygen=blood_oxygen_result,        # 现在是完整Dict
                blood_pressure=blood_pressure_result,    # 现在是完整Dict
                pulse_type=pulse_type,
                timestamp=self._parse_timestamp(raw_data.get('timestamp'))
            )
            
            log_msg = f"简化模式处理完成 - 心率: {heart_rate} bpm"
            if blood_oxygen_result.get('value') is not None:
                log_msg += f", 血氧: {blood_oxygen_result['value']}%"
            logger.info(log_msg)
            
            return {
                'status': 'success',
                'data': result.to_dict()
            }
            
        except Exception as e:
            logger.error(f"简化模式处理失败: {e}", exc_info=True)
            return self._create_error_response(str(e), 'simple')

    def _process_extended_mode(self, raw_data: Dict, ppg_array: np.ndarray, features: Dict) -> Dict:
        """
        扩展模式处理 - 返回完整的分析数据（包含置信度信息）
        
        用于：数据库保存、详细分析、机器学习
        """
        try:
            heart_rate = features['heart_rate']
            
            # 计算健康指标（现在返回Dict）
            ir_data = raw_data.get('ir')
            if ir_data:
                ir_array = np.array(ir_data, dtype=np.float64)
            else:
                ir_array = None
            blood_oxygen_result = self.signal_processor.calculate_blood_oxygen(ppg_array, ir_array)
            blood_pressure_result = self.signal_processor.calculate_blood_pressure(ppg_array, heart_rate)
            
            # 脉象分析
            pulse_type = self.signal_processor.analyze_pulse_type(features)
            
            # 信号质量评估
            signal_quality = self.signal_processor._assess_signal_quality(ppg_array)
            
            # 创建扩展结果
            result = ExtendedPulseData(
                heart_rate=heart_rate,
                hrv_sdnn=features['hrv_sdnn'],
                pulse_strength=features['pulse_strength'],
                pulse_rhythm=features['pulse_rhythm'],
                pulse_type=pulse_type,
                peak_count=features['peak_count'],
                signal_quality=signal_quality,
                blood_oxygen=blood_oxygen_result,        # 现在是完整Dict
                blood_pressure=blood_pressure_result,    # 现在是完整Dict
                timestamp=self._parse_timestamp(raw_data.get('timestamp'))
            )
            
            logger.info(f"扩展模式处理完成 - 心率: {heart_rate} bpm, 数据包含置信度信息")
            
            return {
                'status': 'success',
                'data': result.to_dict(),
                'user_id': raw_data.get('user_id')
            }
            
        except Exception as e:
            logger.error(f"扩展模式处理失败: {e}", exc_info=True)
            return self._create_error_response(str(e), 'extended')

    def extract_waveform_data(self, raw_data: Dict, window_size: int = 100) -> WaveformData:
        """
        提取波形数据用于实时推送

        Args:
            raw_data: 原始数据
            window_size: 窗口大小（采样点数），默认100点（1秒@100Hz）

        Returns:
            波形数据对象
        """
        try:
            ppg_data = raw_data.get('ppg', [])
            
            # 取最后window_size个点
            ppg_samples = ppg_data[-window_size:] if len(ppg_data) > 0 else []
            
            # 尝试计算当前心率
            heart_rate = None
            if len(ppg_samples) > 50:
                try:
                    heart_rate, _ = self.signal_processor.calculate_heart_rate(
                        np.array(ppg_samples, dtype=np.float64)
                    )
                except:
                    pass
            
            waveform = WaveformData(
                timestamp=self._parse_timestamp(raw_data.get('timestamp')),
                ppg_samples=ppg_samples,
                heart_rate=heart_rate
            )
            
            return waveform
            
        except Exception as e:
            logger.error(f"波形提取失败: {e}")
            return WaveformData(
                timestamp=int(datetime.now().timestamp()),
                ppg_samples=[],
                heart_rate=None
            )

    def _validate_signal(self, signal_data: np.ndarray) -> bool:
        """
        验证信号质量

        Args:
            signal_data: 信号数组

        Returns:
            是否合格
        """
        try:
            # 检查是否有效值
            if np.isnan(signal_data).any() or np.isinf(signal_data).any():
                logger.warning("信号包含无效值")
                return False

            # 检查信号变化范围
            signal_range = np.ptp(signal_data)  # peak to peak
            if signal_range < 10:  # 阈值需要根据实际调整
                logger.warning(f"信号变化范围过小: {signal_range}")
                return False

            # 检查是否全为常数
            if np.std(signal_data) < 1:
                logger.warning("信号无变化")
                return False

            return True

        except Exception as e:
            logger.error(f"信号验证失败: {e}")
            return False

    def _create_error_response(self, error_msg: str, mode: str = 'simple') -> Dict:
        """
        创建错误响应

        Args:
            error_msg: 错误信息
            mode: 响应模式

        Returns:
            错误响应字典
        """
        return {
            'status': 'error',
            'message': error_msg
        }

    def _parse_timestamp(self, timestamp_input: Optional[Any]) -> int:
        """
        解析时间戳
        
        Args:
            timestamp_input: 可能是字符串或int
            
        Returns:
            Unix时间戳（整数）
        """
        try:
            if isinstance(timestamp_input, int):
                return timestamp_input
            elif isinstance(timestamp_input, str):
                # 尝试解析各种格式
                from dateutil import parser
                dt = parser.parse(timestamp_input)
                return int(dt.timestamp())
        except:
            pass
        
        # 默认返回当前时间戳
        return int(datetime.now().timestamp())

    def generate_mock_data(self, user_id: int = 1) -> Dict[str, Any]:
        """
        生成模拟数据（用于测试）

        Args:
            user_id: 用户ID

        Returns:
            模拟的原始数据（包含PPG和IR通道）
        """
        # 生成10秒的模拟PPG信号（100Hz采样率）
        t = np.linspace(0, 10, 1000)

        # 模拟心率75bpm的PPG信号
        target_heart_rate = 75
        frequency = target_heart_rate / 60  # Hz

        # PPG（Red）通道
        ppg_signal = 100 + 50 * np.sin(2 * np.pi * frequency * t)
        ppg_signal += np.random.normal(0, 2, len(t))  # 添加噪声
        ppg_signal += 20 * np.sin(4 * np.pi * frequency * t)  # 二次谐波

        # IR（Infrared）通道 - 与PPG相关但幅度不同
        # 通常IR的直流分量更大
        ir_signal = 150 + 30 * np.sin(2 * np.pi * frequency * t)
        ir_signal += np.random.normal(0, 1.5, len(t))  # 更小的噪声
        ir_signal += 10 * np.sin(4 * np.pi * frequency * t)

        mock_data = {
            'ppg': ppg_signal.tolist(),
            'ir': ir_signal.tolist(),  # 包含IR数据用于计算血氧
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id
        }

        logger.info(f"生成模拟数据，用户ID: {user_id}，心率: {target_heart_rate} bpm")
        return mock_data