"""
LLM 合成服务 - 将四诊结果合成为综合诊断建议
支持调用本地或外部 LLM API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os
from dataclasses import dataclass
import anthropic
import os

router = APIRouter(prefix="/api/synthesis", tags=["synthesis"])

@dataclass
class DiagnosisInfo:
    """诊断信息数据结构"""
    patientName: str
    gender: str
    age: int
    diagnoses: Dict[str, Any]


class SynthesisRequest(BaseModel):
    """LLM合成请求模型"""
    patientName: str
    gender: str
    age: int
    diagnoses: Dict[str, Any]


def build_tcm_prompt(diagnosis_info: Dict[str, Any]) -> str:
    """
    构建TCM诊断合成提示词
    将四诊结果组织成结构化的提示词，指导LLM进行综合判断
    """
    
    prompt = """你是一名专业的中医四诊专家。

我现在将提供一个患者的四诊检查结果（望诊、闻诊、问诊、切诊），请你基于这些结果进行综合分析，给出中医调理建议。

## 患者基本信息
"""
    
    prompt += f"- 姓名：{diagnosis_info.get('patientName', '未知')}\n"
    prompt += f"- 性别：{diagnosis_info.get('gender', '未知')}\n"
    prompt += f"- 年龄：{diagnosis_info.get('age', '未知')}岁\n\n"
    
    prompt += "## 四诊检查结果\n\n"
    
    diagnoses = diagnosis_info.get('diagnoses', {})
    
    # 望诊（舌象）
    if 'wang' in diagnoses:
        wang = diagnoses['wang']
        prompt += "### 望诊（舌象分析）\n"
        prompt += f"- 舌象描述：{wang.get('result', '未记录')}\n\n"
    
    # 闻诊（音频分析）
    if 'wen_audio' in diagnoses:
        wen = diagnoses['wen_audio']
        prompt += "### 闻诊（音频分析）\n"
        prompt += f"- 诊断结论：{wen.get('conclusion', '未记录')}\n"
        prompt += f"- 置信度：{wen.get('confidence', 0):.2f}\n"
        if 'tags' in wen:
            prompt += f"- 体质标签：{', '.join(wen['tags']) if isinstance(wen['tags'], list) else str(wen['tags'])}\n"
        prompt += "\n"
    
    # 问诊（问卷调查）
    if 'wen_questionnaire' in diagnoses:
        wenQ = diagnoses['wen_questionnaire']
        prompt += "### 问诊（症状调查）\n"
        prompt += f"- 问卷结论：{wenQ.get('conclusion', '未记录')}\n"
        if 'scores' in wenQ:
            prompt += f"- 评分数据：{wenQ['scores']}\n"
        prompt += "\n"
    
    # 切诊（脉搏）
    if 'qie' in diagnoses:
        qie = diagnoses['qie']
        prompt += "### 切诊（脉搏检测）\n"
        prompt += f"- 心率：{qie.get('heartRate', 'N/A')} bpm\n"
        prompt += f"- 血氧：{qie.get('spo2', 'N/A')}%\n"
        prompt += f"- 信号有效率：{qie.get('validRate', 'N/A')}%\n"
        if qie.get('tcmSuggestion'):
            prompt += f"- TCM建议：{qie['tcmSuggestion']}\n"
        prompt += "\n"
    
    # 诊断指示
    prompt += """## 分析要求

请基于上述四诊结果进行综合分析，按照以下格式输出：

### 1. 体质判断
根据四诊结果判断患者的中医体质类型（如平和质、气虚质、阳虚质、阴虚质、痰湿质、湿热质、血瘀质、气郁质、特禀质等）

### 2. 主要证型分析  
描述患者的主要中医证型，包括：
- 主要症状特点
- 证型判断依据
- 可能的证型组合

### 3. 调理建议
给出3-5条具体的中医调理建议，包括：
- 饮食调理（推荐食物/禁忌食物）
- 生活起居（作息、作息调理）
- 运动保健（适宜的运动方式）
- 穴位保健（可以按摩的穴位及方法）
- 必要时建议中医药调理方向

### 4. 注意事项
列出需要特别注意的要点和禁忌

### 5. 建议复诊周期
根据患者情况建议适当的复诊周期

输出格式使用Markdown，保持清晰的结构和易读的格式。
"""
    
    return prompt


def call_claude_api(messages: list, system_prompt: str = None) -> str:
    """
    调用 Anthropic Claude API
    """
    try:
        client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=system_prompt or "You are a helpful assistant.",
            messages=messages
        )
        
        return response.content[0].text
    except Exception as e:
        print(f"[ERROR] Claude API调用失败: {str(e)}")
        raise


def generate_tcm_synthesis(diagnosis_info: Dict[str, Any]) -> str:
    """
    调用LLM生成TCM诊断合成
    """
    try:
        # 构建提示词
        prompt = build_tcm_prompt(diagnosis_info)
        
        # 调用Claude API
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        synthesis = call_claude_api(messages)
        return synthesis
        
    except Exception as e:
        print(f"[ERROR] LLM合成失败: {str(e)}")
        # 返回回退方案
        return generate_fallback_synthesis(diagnosis_info)


def generate_fallback_synthesis(diagnosis_info: Dict[str, Any]) -> str:
    """
    当LLM不可用时的回退方案
    """
    synthesis = "## 综合四诊诊断建议\n\n"
    
    diagnoses = diagnosis_info.get('diagnoses', {})
    
    if 'wang' in diagnoses:
        synthesis += f"### 舌象诊断\n{diagnoses['wang'].get('result', '暂无诊断')}\n\n"
    
    if 'wen_audio' in diagnoses:
        synthesis += f"### 体质诊断\n根据音频分析，患者属于 {diagnoses['wen_audio'].get('conclusion', '平和体质')}\n\n"
    
    if 'wen_questionnaire' in diagnoses:
        synthesis += f"### 问诊结论\n{diagnoses['wen_questionnaire'].get('conclusion', '暂无诊断')}\n\n"
    
    if 'qie' in diagnoses:
        qie = diagnoses['qie']
        synthesis += f"### 脉搏数据\n- 心率: {qie.get('heartRate', 'N/A')} bpm\n- 血氧: {qie.get('spo2', 'N/A')}%\n\n"
    
    synthesis += """### 调理建议
1. 保持作息规律，早睡早起
2. 适度增加运动，建议散步或太极
3. 饮食清淡，避免辛辣刺激食物
4. 定期复诊，监测体质变化
"""
    
    return synthesis


@router.post("/llm")
async def synthesize_diagnosis(request: SynthesisRequest):
    """
    POST /api/synthesis/llm
    调用LLM进行四诊综合诊断
    """
    print("[DEBUG] 开始LLM诊断合成...")
    
    try:
        # 转换为字典
        diagnosis_info = request.model_dump()
        
        # 调用LLM生成综合诊断
        synthesis = generate_tcm_synthesis(diagnosis_info)
        
        print("[SUCCESS] LLM合成完成")
        
        return {
            "code": 200,
            "msg": "诊断合成成功",
            "synthesis": synthesis
        }
    
    except Exception as e:
        print(f"[ERROR] LLM合成异常: {str(e)}")
        
        # 返回回退方案
        try:
            synthesis = generate_fallback_synthesis(request.model_dump())
            return {
                "code": 200,
                "msg": "使用备选方案生成诊断",
                "synthesis": synthesis
            }
        except Exception as fallback_e:
            print(f"[ERROR] 回退方案也失败: {str(fallback_e)}")
            raise HTTPException(status_code=500, detail="诊断合成失败")
