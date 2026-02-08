# main_with_hardware.py - 集成Arduino硬件的FastAPI应用

"""
完整的脉诊分析系统 - 包含Arduino硬件数据接收

使用方式:
  python main_with_hardware.py --port COM3  # Windows
  python main_with_hardware.py --port /dev/ttyUSB0  # Linux
"""

import argparse
import logging
from fastapi import FastAPI
import uvicorn
import threading

from config import config
from api import router_pulse
from utils import setup_logger, SerialDataReceiver

# 初始化日志
setup_logger()
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="脉诊 AI 诊断服务（含硬件支持）")

# 注册脉诊路由
app.include_router(router_pulse.router)

# 硬件相关全局变量
serial_receiver = None
HARDWARE_CONNECTED = False


def initialize_hardware(port=None):
    """
    初始化硬件连接
    
    Args:
        port: 串口号 (如'COM3'), 如果为None则自动检测
    """
    global serial_receiver, HARDWARE_CONNECTED
    
    try:
        logger.info("=" * 50)
        logger.info("正在初始化硬件连接...")
        
        
        # 创建串口接收器
        serial_receiver = SerialDataReceiver(port=port, baudrate=115200)
        
        # 连接硬件
        if not serial_receiver.connect():
            logger.warning("❌ 硬件连接失败 - 系统将运行在手动API模式")
            return False
        
        # 启动接收线程
        serial_receiver.start_receiving(callback=on_hardware_data_received)
        HARDWARE_CONNECTED = True
        
        logger.info("✓ 硬件连接成功")
        logger.info("=" * 50)
        return True
        
    except Exception as e:
        logger.error(f"硬件初始化异常: {e}")
        return False


def on_hardware_data_received(raw_data: dict):
    """
    硬件数据接收回调
    
    当Arduino发送数据时触发此函数
    """
    try:
        from core import PulseDataProcessor
        from utils import SpringBootClient
        
        pulse_processor = PulseDataProcessor()
        spring_boot_client = SpringBootClient()
        
        logger.info(f"✓ 收到硬件数据: {len(raw_data.get('ir', []))} 个采样点")
        
        # 填充必要的字段
        raw_data['ppg'] = raw_data.get('ir', [])  # 使用IR作为PPG数据
        raw_data['user_id'] = raw_data.get('user_id', 1)
        
        # 处理数据（简化模式，用于实时显示）
        result = pulse_processor.process_raw_data(raw_data, mode='simple')
        
        if result['status'] == 'success':
            logger.info(f"✓ 数据处理成功: 心率={result['data']['heart_rate']} bpm")
            
            # 发送到Spring Boot后端（可选）
            try:
                spring_boot_client.send_pulse_data(result['data'])
            except Exception as e:
                logger.warning(f"发送到Spring Boot失败: {e}")
        else:
            logger.warning(f"❌ 数据处理失败: {result['message']}")
            
    except Exception as e:
        logger.error(f"处理硬件数据异常: {e}", exc_info=True)


# ===== 硬件状态端点 =====

@app.get("/hardware/status")
async def hardware_status():
    """查询硬件连接状态"""
    return {
        'connected': HARDWARE_CONNECTED,
        'port': serial_receiver.port if serial_receiver else None,
        'baudrate': 115200
    }


@app.post("/hardware/connect")
async def connect_hardware(data: dict):
    """
    后期连接硬件
    
    请求格式: {"port": "COM3"}
    """
    global serial_receiver, HARDWARE_CONNECTED
    
    try:
        port = data.get('port')
        
        if HARDWARE_CONNECTED:
            return {
                'status': 'error',
                'message': '硬件已连接'
            }
        
        if not initialize_hardware(port):
            return {
                'status': 'error',
                'message': '硬件连接失败'
            }
        
        return {
            'status': 'success',
            'message': '硬件连接成功',
            'port': serial_receiver.port
        }
        
    except Exception as e:
        logger.error(f"连接硬件异常: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


# ===== 应用启动 =====

def main():
    """应用入口"""
    parser = argparse.ArgumentParser(description='脉诊实时监测系统')
    parser.add_argument('--port', type=str, default=None, help='Arduino串口号 (如COM3)')
    parser.add_argument('--no-hardware', action='store_true', help='不使用硬件连接，仅API模式')
    
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info("脉诊实时监测系统 v2.0")
    logger.info("=" * 50)
    
    # 初始化硬件连接（除非明确指定不使用）
    if not args.no_hardware:
        initialize_hardware(args.port)
    else:
        logger.info("启动模式: 手动API模式 (无硬件)")
    
    logger.info(f"监听地址: {config.HOST}:{config.PORT}")
    logger.info("=" * 50)
    
    # 启动FastAPI应用
    uvicorn.run(app, host=config.HOST, port=config.PORT)


if __name__ == '__main__':
    main()
