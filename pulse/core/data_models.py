# core/data_models.py - 数据模型定义

from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Union
from datetime import datetime


@dataclass
class BloodPressure:
    """血压数据"""
    systolic: Optional[float] = None  # 收缩压
    diastolic: Optional[float] = None  # 舒张压

    def to_dict(self) -> Dict:
        if self.systolic is None or self.diastolic is None:
            return None
        return {
            "sys": self.systolic,
            "dia": self.diastolic
        }


@dataclass
class PulseAnalysisResult:
    """脉诊简化结果 - 核心5个字段（包含置信度信息）"""
    heart_rate: float  # 心率 (bpm)
    blood_oxygen: Optional[Union[float, Dict]] = None  # 血氧：可以是float或Dict（含置信度）
    blood_pressure: Optional[Union[Dict, 'BloodPressure']] = None  # 血压：可以是Dict或BloodPressure
    pulse_type: str = ""  # 脉象分类，如"平脉"、"数脉"
    timestamp: int = None  # Unix时间戳

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = int(datetime.now().timestamp())

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        result = {
            "heart_rate": round(self.heart_rate, 1),
            "pulse_type": self.pulse_type,
            "timestamp": self.timestamp
        }
        
        # 处理血氧（可能是float或Dict）
        if self.blood_oxygen is not None:
            if isinstance(self.blood_oxygen, dict):
                result["blood_oxygen"] = self.blood_oxygen  # 保持Dict结构（包含置信度等）
            else:
                result["blood_oxygen"] = round(self.blood_oxygen, 1)
        
        # 处理血压（可能是BloodPressure对象或Dict）
        if self.blood_pressure is not None:
            if isinstance(self.blood_pressure, dict):
                result["blood_pressure"] = self.blood_pressure  # 保持Dict结构（包含置信度等）
            elif isinstance(self.blood_pressure, BloodPressure):
                bp_dict = self.blood_pressure.to_dict()
                if bp_dict is not None:
                    result["blood_pressure"] = bp_dict
        
        return result


@dataclass
class WaveformData:
    """实时波形数据 - 用于前端可视化"""
    timestamp: int  # Unix时间戳
    ppg_samples: List[float]  # PPG采样点（最近100ms左右）
    heart_rate: Optional[float] = None  # 当前估算的心率，可选

    def to_dict(self) -> Dict:
        return {
            "type": "waveform",
            "timestamp": self.timestamp,
            "ppg_samples": self.ppg_samples,
            "heart_rate": round(self.heart_rate, 1) if self.heart_rate else None
        }


@dataclass
class ExtendedPulseData:
    """扩展脉诊数据 - 用于详细分析（可选，包含置信度信息）"""
    heart_rate: float
    hrv_sdnn: float  # 心率变异性
    pulse_strength: float  # 脉搏强度（振幅）
    pulse_rhythm: str  # 脉律："regular" 或 "irregular"
    pulse_type: str  # 脉象分类
    peak_count: int  # 检测到的心搏峰值数
    signal_quality: str  # 信号质量："good"、"fair"、"poor"
    blood_oxygen: Optional[Union[float, Dict]] = None  # 血氧：可以是float或Dict（含置信度）
    blood_pressure: Optional[Union[Dict, 'BloodPressure']] = None  # 血压：可以是Dict或BloodPressure
    timestamp: int = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = int(datetime.now().timestamp())

    def to_dict(self) -> Dict:
        result = {
            "heart_rate": round(self.heart_rate, 1),
            "hrv_sdnn": round(self.hrv_sdnn, 2),
            "pulse_strength": round(self.pulse_strength, 2),
            "pulse_rhythm": self.pulse_rhythm,
            "pulse_type": self.pulse_type,
            "peak_count": self.peak_count,
            "signal_quality": self.signal_quality,
            "timestamp": self.timestamp
        }
        
        # 处理血氧（可能是float或Dict）
        if self.blood_oxygen is not None:
            if isinstance(self.blood_oxygen, dict):
                result["blood_oxygen"] = self.blood_oxygen  # 保持Dict结构
            else:
                result["blood_oxygen"] = round(self.blood_oxygen, 1)
        
        # 处理血压（可能是BloodPressure对象或Dict）
        if self.blood_pressure is not None:
            if isinstance(self.blood_pressure, dict):
                result["blood_pressure"] = self.blood_pressure  # 保持Dict结构
            elif isinstance(self.blood_pressure, BloodPressure):
                bp_dict = self.blood_pressure.to_dict()
                if bp_dict is not None:
                    result["blood_pressure"] = bp_dict
        
        return result


@dataclass
class APIResponse:
    """API统一响应格式"""
    status: str  # "success" 或 "error"
    data: Optional[Dict] = None  # 响应数据
    message: str = ""  # 错误或提示信息

    def to_dict(self) -> Dict:
        result = {"status": self.status}
        if self.data:
            result["data"] = self.data
        if self.message:
            result["message"] = self.message
        return result
