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
    llmContext: Optional[Dict[str, Any]] = None


FOCUS_LABELS = {
    "balanced": "平衡综合",
    "qie": "切诊（脉诊）优先",
    "wang": "望诊（舌诊）优先",
    "wen_audio": "闻诊（声音）优先",
    "wen_questionnaire": "问诊（问卷）优先",
}

CORE_DIAG_KEYS = ["wang", "wen_audio", "wen_questionnaire", "qie"]

DEFAULT_SYSTEM_PROMPT = """你是资深中医四诊合参医生，擅长将算法输出与中医辨证进行联合推理。
当用户未指定侧重板块时，输出常规综合诊断，简明、克制、可执行。
仅当用户明确指定侧重板块时，才进行详细复核并展开证据链分析。
输出必须为中文 Markdown。"""


def normalize_focus_mode(raw_focus: Optional[str]) -> str:
    if not raw_focus:
        return "balanced"
    focus = str(raw_focus).strip().lower()
    if focus in {"none", "no_focus", "no-focus", "nofocus", "不侧重", "综合", "综合分析"}:
        return "balanced"
    return focus if focus in FOCUS_LABELS else "balanced"


def build_algorithm_guidance(diagnoses: Dict[str, Any], focus_mode: str) -> str:
    guidance = [
        "## 算法结果再解读要求",
        "- 必须优先引用各板块已有算法结论，再做中医证候推理。",
    ]

    if focus_mode != "balanced":
        guidance.append("- 侧重板块采用详细复核结构：关键数据 -> 算法含义 -> 中医解释 -> 建议。")
    else:
        guidance.append("- 未指定侧重时使用常规简版结构：核心发现 -> 证候判断 -> 调理建议。")

    if "wang" in diagnoses:
        guidance.append("- 望诊：重点使用 result、tongueMetrics 进行舌象再解读，逐条解释每个舌像维度对应的证据与证候。")
    if "wen_audio" in diagnoses:
        guidance.append("- 闻诊：重点使用 conclusion、confidence、tags、features，先解释音频特征含义，再映射到体质/证候。")
    if "wen_questionnaire" in diagnoses:
        guidance.append("- 问诊：重点使用 conclusion、scores、constitutionProfile，解释高分体质簇与证候倾向关联。")
    if "qie" in diagnoses:
        guidance.append("- 切诊：重点使用 heartRate、spo2、validRate、sampleCount、qualityLevel、heartRateBand、spo2Band、tcmSuggestion；若存在 keyMetrics（hrv_rmssd_ms/rhythm_cv/perfusion_index/signal_quality/pulse_tags）需优先用于脉象细化推断。")

    if focus_mode != "balanced":
        guidance.append(f"- 当前为侧重模式：{FOCUS_LABELS.get(focus_mode, FOCUS_LABELS['balanced'])}，该板块需给出、最细、最完整的复核分析。")

    guidance.append("")
    return "\n".join(guidance)


def build_output_requirements(focus_mode: str) -> str:
    if focus_mode == "balanced":
        focus_rule = "各板块篇幅尽量均衡（约 25%:25%:25%:25%）。"
        section_2 = "2. 四诊常规综合：每个板块给核心结论与简要建议（每板块 2-4 句）。"
        section_3 = "3. 综合判断：给出体质/证候倾向与主要依据（简要列点）。"
        section_4 = "4. 调理建议：饮食、作息、运动（每项 1-2 条，避免冗长）。"
        section_5 = "5. 数据缺口提示：一次性列出所有缺失板块，并给出补充检查建议。"
    else:
        focus_rule = "侧重板块约占 70% 篇幅，其余三个板块共约 30%（每个板块保留核心结论即可）。"
        section_2 = "2. 侧重板块深度复核：包含关键数据摘录、算法结果解读、中医证候推理、风险点、调理建议。"
        section_3 = "3. 其余板块复核：每个板块给核心发现与简要建议。"
        section_4 = "4. 体质判断与证型结论：必须写明依据来自哪些板块和哪些字段。"
        section_5 = "5. 个性化调理方案：饮食、作息、运动、穴位/经络、复诊周期。"

    lines = [
        "## 输出要求",
        f"- 篇幅分配：{focus_rule}",
        "1. 结论摘要（3-5条，先给结论再给证据）。",
        section_2,
        section_3,
        section_4,
        section_5,
        "",
    ]
    return "\n".join(lines)


def build_llm_context_section(diagnosis_info: Dict[str, Any]) -> str:
    llm_context = diagnosis_info.get("llmContext")
    if not llm_context:
        return ""

    lines = [
        "## 字段说明与算法说明（高优先级解释依据）",
        "- 先按字段说明理解数据语义，再做算法解读和中医辨证。",
        "- 不得自创字段含义；如字段说明与直觉冲突，以说明为准。",
        json.dumps(llm_context, ensure_ascii=False, indent=2),
        "",
    ]
    return "\n".join(lines)


def build_tcm_prompt(diagnosis_info: Dict[str, Any]) -> str:
    diagnoses = diagnosis_info.get("diagnoses", {}) or {}
    completed_count = len([k for k in diagnoses.keys() if k in CORE_DIAG_KEYS])
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

    is_focus_mode = focus_mode in {"wang", "wen_audio", "wen_questionnaire", "qie"}

    lines = [
        "你是专业中医四诊合参医生。",
        "请基于给定数据输出诊断结论，不得编造。",
        "",
        "## 患者基本信息",
        f"- 姓名：{diagnosis_info.get('patientName', '未知')}",
        f"- 性别：{diagnosis_info.get('gender', '未知')}",
        f"- 年龄：{diagnosis_info.get('age', '未知')}岁",
        "",
        "## 任务目标",
        "- 在既有四诊数据基础上给出可信、可执行的中医综合结论。",
        "- 重点输出：算法结果含义、中医辨证逻辑、可执行调理方案。",
        "",
        "## 分析侧重与详细程度",
        f"- 当前策略：{focus_label}",
    ]
    
    # 根据侧重点添加详细指示
    if is_focus_mode:
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
        lines.append("- 分析方式：四诊平衡综合，采用常规输出，不做详细复核。")

    custom_prompt = diagnosis_info.get("customPromptTemplate")
    if custom_prompt and str(custom_prompt).strip():
        lines.extend([
            "",
            "## 前端自定义提示词（最高优先级）",
            str(custom_prompt).strip()[:3000],
            "- 执行规则：在不违背事实数据的前提下，优先遵循该提示词的表达风格与关注点（建议占分析策略约60%权重）。",
            "",
        ])
    
    lines.extend([
        "- 若未指定侧重板块，必须执行四诊均衡常规输出，不得默认放大任一板块。",
        "- 仅当存在有效 focusMode（wang/wen_audio/wen_questionnaire/qie）时，才进入详细复核。",
        "",
        build_llm_context_section(diagnosis_info),
        "## 四诊数据（唯一事实来源）",
        json.dumps(diagnoses, ensure_ascii=False, indent=2),
        "",
    ])

    lines.append(build_algorithm_guidance(diagnoses, focus_mode))

    if completed_count < 4:
        lines.append(f"当前缺失板块：{', '.join(missing)}。对缺失板块只给补充检查建议。")
        lines.append("")

    lines.extend([
        build_output_requirements(focus_mode),
        "## 硬性约束",
        "1. 只能基于给定数据，禁止编造。",
        "2. 必须明确区分：事实数据、算法结论、模型推断，三者不可混写为同一层级。",
        "3. 自定义提示词与数据冲突时，以数据为准。",
        "4. 若已指定侧重但该板块缺失或数据质量不足，必须明确说明并降低结论置信度。",
        "5. 使用 Markdown 输出。",
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
        return call_deepseek_api(messages, system_prompt=DEFAULT_SYSTEM_PROMPT)
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
            call_deepseek_api_stream(messages, system_prompt=DEFAULT_SYSTEM_PROMPT, fallback_text=fallback_text),
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
