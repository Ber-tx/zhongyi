from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from core.sound_analyzer import SoundAnalyzer
import logging

router = APIRouter(prefix="/wen", tags=["闻诊"])
logger = logging.getLogger(__name__)

# 初始化
try:
    analyzer = SoundAnalyzer()
except Exception as e:
    logger.error(f"音频分析器初始化失败: {str(e)}")
    analyzer = None


@router.post("/analyze")
async def analyze_sound(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    patient_idcard: str = Form(...)
):
    """
    闻诊音频分析端点
    
    请求参数:
    - file: 音频文件 (multipart/form-data)
    - patient_id: 病人 ID
    - patient_idcard: 病人身份证号
    
    返回:
    {
        "success": bool,
        "data": {
            "main_finding": str,          # 主要体质判断
            "confidence": float,          # 置信度 (0-1)
            "constitution_tags": list,    # 体质标签
            "details": list               # 详细分析
        }
    }
    """
    
    if analyzer is None:
        return {"success": False, "msg": "系统启动中或加载异常"}

    try:
        # 验证病人信息
        if not patient_id or not patient_idcard:
            return {
                "success": False,
                "msg": "缺少病人信息"
            }
        
        logger.info(f"接收闻诊请求: 病人ID={patient_id}, 文件={file.filename}")
        
        # 读取文件内容
        audio_bytes = await file.read()
        
        if len(audio_bytes) == 0:
            return {
                "success": False,
                "msg": "音频文件为空"
            }
        
        logger.info(f"音频文件大小: {len(audio_bytes)} bytes")
        
        # 调用分析器
        result = analyzer.analyze(audio_bytes)
        
        return result
        
    except Exception as e:
        logger.error(f"闻诊分析异常: {str(e)}", exc_info=True)
        return {
            "success": False,
            "msg": "算法引擎内部错误: " + str(e)
        }
