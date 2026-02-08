from pydantic import BaseModel
from typing import List, Optional

# 给 Vue3 的实时数据包
class RealTimeData(BaseModel):
    ir_wave: List[int]      # 原始波形
    hr: Optional[float]     # 实时心率
    spo2: Optional[float]   # 实时血氧
    quality: float          # 信号质量(0.0-1.0)
    is_valid: bool          # 测量是否有效

# 给 Spring Boot 的最终报告数据包
class PulseReport(BaseModel):
    user_id: int
    avg_hr: float
    avg_spo2: float
    raw_data_json: str      # 完整的原始波形数据，用于中医回溯分析
    suggestion: str         # 算法初步判断（如：脉象滑数、脉象沉细）
    measured_at: int        # 时间戳