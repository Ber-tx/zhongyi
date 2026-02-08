# api/router_pulse.py - 脉诊路由处理

from fastapi import APIRouter, HTTPException
import logging
from core import PulseDataProcessor
from utils import SpringBootClient
from config import config

router = APIRouter(prefix="/pulse", tags=["脉诊"])
logger = logging.getLogger(__name__)

# 初始化组件
pulse_processor = PulseDataProcessor()
spring_boot_client = SpringBootClient()


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        'status': 'healthy',
        'service': 'pulse-analysis-service',
        'version': '1.0.0'
    }


@router.post("/receive")
async def receive_pulse_data(raw_data: dict):
    """
    接收硬件（ESP32）发来的原始脉诊数据

    请求格式:
    {
        "ppg": [123, 456, 789, ...],
        "ir": [234, 567, 890, ...],  # 可选
        "timestamp": "2024-01-01 12:00:00",
        "user_id": 1
    }
    
    响应格式（简化版，5个核心字段）:
    {
        "status": "success",
        "data": {
            "heart_rate": 75,
            "blood_oxygen": 98,
            "blood_pressure": {"sys": 120, "dia": 80},
            "pulse_type": "平脉",
            "timestamp": 1706000000
        }
    }
    """
    try:
        if not raw_data:
            logger.warning("收到空数据")
            raise HTTPException(status_code=400, detail={'status': 'error', 'message': '数据为空'})

        logger.info(f"收到原始数据 - 用户ID: {raw_data.get('user_id', 'unknown')}, "
                    f"数据点数: {len(raw_data.get('ppg', []))}")

        # 处理数据 - 使用简化模式
        result = pulse_processor.process_raw_data(raw_data, mode='simple')

        if result.get('status') == 'success':
            # 同时发送到Spring Boot进行存储
            spring_boot_data = pulse_processor.process_raw_data(raw_data, mode='extended')
            if spring_boot_data.get('status') == 'success':
                spring_boot_client.send_pulse_data(spring_boot_data.get('data'))

            return result
        else:
            raise HTTPException(status_code=400, detail=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"接收数据异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        })


@router.post("/test")
async def test_service():
    """测试服务是否正常"""
    try:
        # 测试信号处理
        import numpy as np
        test_signal = np.random.randn(500)
        features = pulse_processor.signal_processor.extract_features(test_signal)

        # 测试Spring Boot连接
        sb_connected = spring_boot_client.test_connection()

        return {
            'status': 'success',
            'signal_processor': 'working',
            'spring_boot_connection': 'connected' if sb_connected else 'disconnected',
            'test_features': features
        }

    except Exception as e:
        logger.error(f"服务测试失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={
            'status': 'error',
            'message': str(e)
        })
