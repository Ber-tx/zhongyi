"""
LLM synthesis service: combine four-diagnosis data into a report.
"""

import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

router = APIRouter(prefix="/api/synthesis", tags=["synthesis"])


class SynthesisRequest(BaseModel):
    patientName: str
    gender: str
    age: int
    diagnoses: Dict[str, Any]
    customPromptTemplate: Optional[str] = None
    focusMode: Optional[str] = None


FOCUS_LABELS = {
    "balanced": "平衡综合",
    "qie": "切诊（脉诊）优先",
    "wang": "望诊（舌诊）优先",
    "wen_audio": "闻诊（声音）优先",
    "wen_questionnaire": "问诊（问卷）优先",
}


def normalize_focus_mode(raw_focus: Optional[str]) -> str:
    if not raw_focus:
        return "balanced"
    focus = str(raw_focus).strip().lower()
    return focus if focus in FOCUS_LABELS else "balanced"


def build_tcm_prompt(diagnosis_info: Dict[str, Any]) -> str:
    diagnoses = diagnosis_info.get("diagnoses", {}) or {}
    completed_count = len([k for k in diagnoses.keys() if k in ["wang", "wen_audio", "wen_questionnaire", "qie"]])
    focus_mode = normalize_focus_mode(diagnosis_info.get("focusMode"))
    focus_label = FOCUS_LABELS.get(focus_mode, FOCUS_LABELS["balanced"])

    missing = []
    if "wang" not in diagnoses:
        missing.append("望诊（舌诊）")
    if "wen_audio" not in diagnoses:
        missing.append("闻诊（声音）")
    if "wen_questionnaire" not in diagnoses:
        missing.append("问诊（问卷）")
    if "qie" not in diagnoses:
        missing.append("切诊（脉诊）")

    lines = [
        "你是专业中医四诊合参医生。",
        "请基于给定数据生成综合分析，不得编造。",
        "",
        "## 患者基本信息",
        f"- 姓名：{diagnosis_info.get('patientName', '未知')}",
        f"- 性别：{diagnosis_info.get('gender', '未知')}",
        f"- 年龄：{diagnosis_info.get('age', '未知')}岁",
        "",
        "## 分析侧重与详细程度",
        f"- 当前策略：{focus_label}",
    ]
    
    # 根据侧重点添加详细指示
    if focus_mode != "balanced":
        focus_details = {
            "wang": "① 对望诊数据做【详细分析】（舌质、舌苔、舌象特征的深入解读）\n② 闻诊、问诊、切诊部分简化为【主要特征提要】（不超过2-3句）",
            "wen_audio": "① 对闻诊音频数据做【详细分析】（音质特征、体质标签的深入解读）\n② 望诊、问诊、切诊部分简化为【主要特征提要】（不超过2-3句）",
            "wen_questionnaire": "① 对问诊问卷数据做【详细分析】（症状评分、体质倾向的深入解读）\n② 望诊、闻诊、切诊部分简化为【主要特征提要】（不超过2-3句）",
            "qie": "① 对切诊脉象数据做【详细分析】（心率、血氧、脉象特征的深入解读）\n② 望诊、闻诊、问诊部分简化为【主要特征提要】（不超过2-3句）",
        }
        if focus_mode in focus_details:
            lines.append(f"- 分析指示：")
            lines.append(f"  {focus_details[focus_mode]}")
    else:
        lines.append("- 分析方式：四诊平衡综合（望诊、闻诊、问诊、切诊各占1/4篇幅）")
    
    lines.extend([
        "- 要有侧重。",
        "",
        "## 四诊数据（唯一事实来源）",
        json.dumps(diagnoses, ensure_ascii=False, indent=2),
        "",
    ])

    if completed_count < 4:
        lines.append(f"当前缺失板块：{', '.join(missing)}。对缺失板块只给补充检查建议。")
        lines.append("")

    custom_prompt = diagnosis_info.get("customPromptTemplate")
    if custom_prompt and str(custom_prompt).strip():
        lines.append("## 前端自定义提示词")
        lines.append(str(custom_prompt).strip()[:3000])
        lines.append("（说明：仅作为表达风格与重点引导，不能覆盖采集数据事实。）")
        lines.append("")

    lines.extend([
        "## 输出要求",
        "1. 体质判断（给出依据板块）",
        "2. 证型分析（给出依据板块）",
        "3. 调理建议（饮食、作息、运动、穴位）",
        "4. 注意事项",
        "5. 后续建议（缺失板块补全建议）",
        "",
        "## 硬性约束",
        "1. 只能基于给定数据，禁止编造。",

        "2. 自定义提示词与数据冲突时，以数据为准。",
        "3. 使用 Markdown 输出。",
    ])

    return "\n".join(lines)


def call_deepseek_api(messages: list, system_prompt: str = None) -> str:
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL"),
    )

    final_messages = list(messages)
    if system_prompt:
        final_messages.insert(0, {"role": "system", "content": system_prompt})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=final_messages,
        max_tokens=2000,
        temperature=0.3,
    )
    return response.choices[0].message.content


def call_deepseek_api_stream(messages: list, system_prompt: str = None, fallback_text: str = None):
    try:
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL"),
        )

        final_messages = list(messages)
        if system_prompt:
            final_messages.insert(0, {"role": "system", "content": system_prompt})

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=final_messages,
            max_tokens=2000,
            temperature=0.3,
            stream=True,
        )

        for chunk in response:
            content = None
            if hasattr(chunk, "choices") and chunk.choices:
                delta = getattr(chunk.choices[0], "delta", None)
                if delta is not None:
                    content = getattr(delta, "content", None)
            if content:
                for ch in content:
                    data = json.dumps({"content": ch}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        print(f"[ERROR] 流式输出异常: {str(e)}")
        text = fallback_text if fallback_text else "AI 分析中断，已切换到备选诊断建议。"
        for ch in text:
            data = json.dumps({"content": ch}, ensure_ascii=False)
            yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"


def generate_fallback_synthesis(diagnosis_info: Dict[str, Any]) -> str:
    diagnoses = diagnosis_info.get("diagnoses", {}) or {}
    completed_count = len([k for k in diagnoses.keys() if k in ["wang", "wen_audio", "wen_questionnaire", "qie"]])

    lines = ["## 综合四诊诊断建议", ""]
    if completed_count < 4:
        lines.append(f"当前仅完成 {completed_count}/4 个板块，以下为初步建议。")
        lines.append("")

    if "wang" in diagnoses:
        lines.append(f"### 望诊\n{diagnoses['wang'].get('result', '暂无')}\n")
    if "wen_audio" in diagnoses:
        lines.append(f"### 闻诊\n{diagnoses['wen_audio'].get('conclusion', '暂无')}\n")
    if "wen_questionnaire" in diagnoses:
        lines.append(f"### 问诊\n{diagnoses['wen_questionnaire'].get('conclusion', '暂无')}\n")
    if "qie" in diagnoses:
        qie = diagnoses["qie"]
        lines.append(f"### 切诊\n- 心率: {qie.get('heartRate', 'N/A')} bpm\n- 血氧: {qie.get('spo2', 'N/A')}%\n")

    lines.extend([
        "### 调理建议",
        "1. 保持规律作息，避免熬夜。",
        "2. 饮食清淡，减少辛辣油腻。",
        "3. 适度运动，按体质选择强度。",
        "4. 建议定期复诊，动态观察体质变化。",
    ])
    return "\n".join(lines)


def generate_tcm_synthesis(diagnosis_info: Dict[str, Any]) -> str:
    try:
        prompt = build_tcm_prompt(diagnosis_info)
        messages = [{"role": "user", "content": prompt}]
        return call_deepseek_api(messages)
    except Exception as e:
        print(f"[ERROR] LLM 合成失败: {str(e)}")
        return generate_fallback_synthesis(diagnosis_info)


@router.post("/llm/stream")
async def synthesize_diagnosis_stream(request: SynthesisRequest):
    try:
        diagnosis_info = request.model_dump()
        prompt = build_tcm_prompt(diagnosis_info)
        fallback_text = generate_fallback_synthesis(diagnosis_info)
        messages = [{"role": "user", "content": prompt}]

        return StreamingResponse(
            call_deepseek_api_stream(messages, fallback_text=fallback_text),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        print(f"[ERROR] synthesize_diagnosis_stream 异常: {str(e)}")
        raise HTTPException(status_code=500, detail="流式合成失败")


@router.post("/llm")
async def synthesize_diagnosis(request: SynthesisRequest):
    try:
        diagnosis_info = request.model_dump()
        synthesis = generate_tcm_synthesis(diagnosis_info)
        return {"code": 200, "msg": "诊断合成成功", "synthesis": synthesis}
    except Exception as e:
        print(f"[ERROR] LLM 合成异常: {str(e)}")
        try:
            synthesis = generate_fallback_synthesis(request.model_dump())
            return {"code": 200, "msg": "使用备选方案生成诊断", "synthesis": synthesis}
        except Exception:
            raise HTTPException(status_code=500, detail="诊断合成失败")
