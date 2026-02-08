# main.py - FastAPI应用主入口

from fastapi import FastAPI
import uvicorn
from api import router_pulse
from utils import setup_logger
from config import config
import logging

# 初始化日志
setup_logger()
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="脉诊 AI 诊断服务")

# 注册脉诊路由
app.include_router(router_pulse.router)

logger.info("=" * 50)
logger.info("脉诊服务启动")
logger.info(f"监听地址: {config.HOST}:{config.PORT}")
logger.info(f"Spring Boot地址: {config.SPRING_BOOT_BASE_URL}")
logger.info("=" * 50)

if __name__ == "__main__":
    # 启动在指定端口
    uvicorn.run(app, host=config.HOST, port=config.PORT)