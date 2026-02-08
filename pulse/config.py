# config.py - 配置文件

class Config:
    """应用配置"""

    # 服务配置
    HOST = '0.0.0.0'
    PORT = 5001

    # Spring Boot后端配置
    SPRING_BOOT_HOST = 'localhost'
    SPRING_BOOT_PORT = 8080
    SPRING_BOOT_BASE_URL = f'http://{SPRING_BOOT_HOST}:{SPRING_BOOT_PORT}'

    # API端点
    PULSE_DATA_ENDPOINT = '/api/pulse/data'

    # 数据处理配置
    SAMPLING_RATE = 100  # MAX30102采样率，通常是100Hz
    WINDOW_SIZE = 500  # 滑动窗口大小（5秒数据）

    # 心率范围
    MIN_HEART_RATE = 40
    MAX_HEART_RATE = 200

    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class DevelopmentConfig(Config):
    """开发环境配置"""
    pass


class ProductionConfig(Config):
    """生产环境配置"""
    LOG_LEVEL = 'WARNING'


# 根据环境选择配置
config = DevelopmentConfig()