from fastapi import APIRouter, UploadFile, File, Form
from core.tongue_shizhen import TongueAnalyzer
import logging
import json

router = APIRouter(prefix="/tongue", tags=["舌诊"])
logger = logging.getLogger(__name__)

# 初始化
try:
    analyzer = TongueAnalyzer()
except Exception as e:
    logger.error(f"舌诊引擎加载失败: {str(e)}")
    analyzer = None


@router.post("/detect")
async def detect(
    file: UploadFile = File(...),
    use_llm: str = Form("false"),
):
    """
    舌诊检测端点（双引擎：YOLOv8 + 可选大模型复诊）

    - file: 舌象图片
    - use_llm: "true"/"false" 是否启用大模型复诊（默认 false，仅在四诊合参阶段使用RAG）
    """
    if analyzer is None:
        return {"success": False, "msg": "系统启动中或加载异常"}

    img_bytes = await file.read()
    try:
        use_llm_review = str(use_llm).strip().lower() in {"true", "1", "yes"}
        result = analyzer.analyze(img_bytes, use_llm_review=use_llm_review)
        return result
    except Exception as e:
        logger.error(f"分析异常: {str(e)}")
        return {"success": False, "msg": "算法引擎内部错误"}


@router.get("/yolo/status")
async def yolo_status():
    """YOLO 模型状态检查。"""
    if analyzer is None:
        return {"success": False, "yolo_loaded": False, "msg": "系统未初始化"}
    try:
        _ = analyzer.yolo
        _ = analyzer.annotator
        return {
            "success": True,
            "yolo_loaded": True,
            "annotation_rules": len(analyzer.annotator.knowledge_cards()),
            "llm_model": analyzer._llm_config.get("model", "unknown"),
        }
    except Exception as e:
        return {"success": False, "yolo_loaded": False, "msg": str(e)}
