from fastapi import APIRouter, UploadFile, File
from core.tongue_shizhen import TongueAnalyzer
import logging

router = APIRouter(prefix="/tongue", tags=["舌诊"])
logger = logging.getLogger(__name__)

# 初始化
try:
    analyzer = TongueAnalyzer()
except Exception as e:
    logger.error(f"模型加载失败: {str(e)}")
    analyzer = None


@router.post("/detect")
async def detect(file: UploadFile = File(...)):
    if analyzer is None:
        return {"success": False, "msg": "系统启动中或加载异常"}

    img_bytes = await file.read()
    try:
        result = analyzer.analyze(img_bytes)
        return result
    except Exception as e:
        logger.error(f"分析异常: {str(e)}")
        return {"success": False, "msg": "算法引擎内部错误"}