# utils/logger.py - 日志配置

import logging
import sys
from config import config


def setup_logger():
    """配置日志系统"""

    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))

    # 格式化器
    formatter = logging.Formatter(config.LOG_FORMAT)
    console_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(console_handler)

    # 可选：文件处理器
    # file_handler = logging.FileHandler('pulse_service.log')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    logger.info("日志系统初始化完成")
    return logger