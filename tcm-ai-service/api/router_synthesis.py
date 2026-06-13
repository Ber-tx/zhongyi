"""
LLM synthesis service: combine four-diagnosis data into a report.
支持 RAG（检索增强生成）：合成前先检索知识库，将中医典籍知识注入提示词。
"""

import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel

from core.knowledge_base import KnowledgeBase
from core.knowledge_ingestor import ingest_markdown

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/synthesis", tags=["synthesis"])

# ── 初始化知识库 ──────────────────────────────────────────
try:
    kb = KnowledgeBase()
    logger.info(f"知识库初始化完成，向量数: {kb.count()}")
except Exception as e:
    logger.warning(f"知识库初始化失败: {e}")
    kb = None


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
当用户未指定侧重板块时，输出充分的常规综合诊断，强调跨板块证据整合、风险判断与分层建议。
仅当用户明确指定侧重板块时，才进行详细复核并展开证据链分析。
输出必须为中文 Markdown。"""

LLM_MODEL = "glm-4.5-air"
LLM_MAX_TOKENS = int(os.getenv("GLM_REPORT_MAX_TOKENS", "4096"))


def normalize_focus_mode(raw_focus: Optional[str]) -> str:
    if not raw_focus:
        return "balanced"
    focus = str(raw_focus).strip().lower()
    if focus in {"none", "no_focus", "no-focus", "nofocus", "不侧重", "综合", "综合分析"}:
        return "balanced"
    return focus if focus in FOCUS_LABELS else "balanced"


def build_rag_context(diagnoses: Dict[str, Any]) -> str:
    """
    从知识库检索与当前四诊数据相关的上下文。
    支持中⽂语义搜索（Qwen text-embedding-v4 + ChromaDB）。
    """
    if kb is None or not kb.ready():
        return ""

    # 构建检索 query：从各板块提取关键词
    query_parts = ["中医诊断", "四诊合参"]

    if "wang" in diagnoses:
        wang = diagnoses["wang"]
        result = wang.get("result", "")
        if result:
            query_parts.append(result[:100])
        tm = wang.get("tongueMetrics", {})
        if tm:
            scores_str = json.dumps(tm, ensure_ascii=False)
            query_parts.append(f"舌象:{scores_str[:100]}")

    if "wen_audio" in diagnoses:
        wen = diagnoses["wen_audio"]
        conclusion = wen.get("conclusion", "")
        if conclusion:
            query_parts.append(conclusion[:100])

    if "wen_questionnaire" in diagnoses:
        q = diagnoses["wen_questionnaire"]
        conclusion = q.get("conclusion", "")
        if conclusion:
            query_parts.append(conclusion[:100])

    if "qie" in diagnoses:
        qie = diagnoses["qie"]
        hr = qie.get("heartRate", "")
        spo2 = qie.get("spo2", "")
        if hr or spo2:
            query_parts.append(f"脉诊心率{hr}血氧{spo2}")

    query = " ".join(query_parts)
    query = query[:300]  # 避免过长

    try:
        result = kb.search_with_context(query, top_k=5)
        if result["total"] > 0:
            return (
                "\n\n## 参考知识库（中医典籍检索结果）\n"
                "以下内容来自《中医学》第10版教材，请优先参考这些资料进行辨证分析：\n\n"
                f"{result['context']}\n\n"
                "## 引用说明\n"
                "请在回答中适当引用以上知识库内容作为辨证依据。"
            )
    except Exception as e:
        logger.warning(f"知识库检索失败: {e}")

    return ""


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
        guidance.append(f"- 当前为侧重模式：{FOCUS_LABELS.get(focus_mode, FOCUS_LABELS['balanced'])}，该板块需给出最细、最完整的复核分析。")
    guidance.append("")
    return "\n".join(guidance)


def build_output_requirements(focus_mode: str) -> str:
    if focus_mode == "balanced":
        focus_rule = "各板块篇幅尽量均衡（约 25%:25%:25%:25%）。"
        section_2 = "2. 四诊综合解读：每个已完成板块给核心结论、关键依据与风险提示（每板块 3-5 句）。"
        section_3 = "3. 跨板块证据整合：说明各板块互相支持或冲突的点，并给出取舍理由。"
        section_4 = "4. 体质/证候判断：写清主要结论、次要倾向与结论置信度来源。"
        section_5 = "5. 分层调理建议：给出饮食、作息、运动与复评建议。"
    else:
        focus_rule = "侧重板块约占 80% 篇幅，其余板块总计约 20%（每个非侧重板块仅保留核心结论与1条建议，控制在 1-2 句）。"
        section_2 = "2. 侧重板块深度复核：包含关键数据摘录、算法结果解读、中医证候推理、风险点、调理建议。"
        section_3 = "3. 其余板块复核：每个板块只给极简摘要（核心发现 + 1条建议），不展开证据链。"
        section_4 = '4. 体质判断与证型结论：直接给结论与置信度，不单列"诊断依据/证据链"小节。'
        section_5 = "5. 个性化调理方案：必须完整给出饮食、作息、运动、穴位/经络、复诊周期，并包含明确禁忌。"

    lines = [
        "## 输出要求",
        f"- 篇幅分配：{focus_rule}",
        "1. 结论摘要（3-5条，先给结论再给证据）。",
        section_2,
        section_3,
        section_4,
        section_5,
        '- 完整性要求：不得出现空标题或空条目（例如"禁忌："后无内容）。',
        "- 调理建议最少包含：饮食>=3条、作息>=2条、运动>=2条、穴位/经络>=2条、禁忌>=2条。",
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

    if is_focus_mode:
        focus_details = {
            "wang": "① 对望诊数据做【详细分析】（舌质、舌苔、舌象特征的深入解读）\n② 闻诊、问诊、切诊仅保留【极简提要】（每板块1-2句）",
            "wen_audio": "① 对闻诊音频数据做【详细分析】（音质特征、体质标签的深入解读）\n② 望诊、问诊、切诊仅保留【极简提要】（每板块1-2句）",
            "wen_questionnaire": "① 对问诊问卷数据做【详细分析】（症状评分、体质倾向的深入解读）\n② 望诊、闻诊、切诊仅保留【极简提要】（每板块1-2句）",
            "qie": "① 对切诊脉象数据做【详细分析】（心率、血氧、脉象特征的深入解读）\n② 望诊、闻诊、问诊仅保留【极简提要】（每板块1-2句）",
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
    ])

    # ── RAG 知识库上下文 ──
    rag_context = build_rag_context(diagnoses)
    if rag_context:
        lines.append(rag_context)
        lines.append("")

    lines.extend([
        "## 四诊数据（唯一事实来源）",
        json.dumps(diagnoses, ensure_ascii=False, indent=2),
        "",
    ])

    lines.append(build_algorithm_guidance(diagnoses, focus_mode))

    if (not is_focus_mode) and completed_count < 4:
        lines.append(f"当前缺失板块：{', '.join(missing)}。对缺失板块只给补充检查建议。")
        lines.append("")

    lines.extend([
        build_output_requirements(focus_mode),
        "## 硬性约束",
        "1. 只能基于给定数据，禁止编造，不要一直重复原始数据。",
        "2. 必须明确区分：事实数据、算法结论、模型推断，三者不可混写为同一层级。",
        "3. 自定义提示词与数据冲突时，以数据为准。",
        "4. 若已指定侧重但该板块缺失或数据质量不足，仅在对应板块内简短说明并降低结论置信度，不单独展开缺失提醒段落。",
        '5. 若为侧重模式，禁止单独输出"诊断依据"或"证据链"标题段。',
        '6. 输出前自检：所有小节均需有实质内容，尤其"禁忌"不可留空。',
        "7. 使用 Markdown 输出。",
    ])

    return "\n".join(lines)


def call_deepseek_api(messages: list, system_prompt: str = None) -> str:
    client = OpenAI(
        api_key=os.getenv("GLM_API_KEY"),
        base_url=os.getenv("GLM_BASE_URL"),
    )
    final_messages = list(messages)
    if system_prompt:
        final_messages.insert(0, {"role": "system", "content": system_prompt})
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=final_messages,
        max_tokens=LLM_MAX_TOKENS,
        temperature=0.3,
    )
    return response.choices[0].message.content


def call_deepseek_api_stream(messages: list, system_prompt: str = None, fallback_text: str = None):
    try:
        client = OpenAI(
            api_key=os.getenv("GLM_API_KEY"),
            base_url=os.getenv("GLM_BASE_URL"),
        )
        final_messages = list(messages)
        if system_prompt:
            final_messages.insert(0, {"role": "system", "content": system_prompt})
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=final_messages,
            max_tokens=LLM_MAX_TOKENS,
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
                data = json.dumps({"content": content}, ensure_ascii=False)
                yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        print(f"[ERROR] 流式输出异常: {str(e)}")
        text = fallback_text if fallback_text else "AI 分析中断，已切换到备选诊断建议。"
        data = json.dumps({"content": text}, ensure_ascii=False)
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


# ── 原有四诊合参端点 ──────────────────────────────────────

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


# ── 知识库管理端点 ─────────────────────────────────────────

@router.get("/knowledge/status")
async def knowledge_status():
    """知识库状态检查。"""
    if kb is None:
        return {"success": False, "ready": False, "vector_count": 0, "msg": "知识库未初始化"}
    try:
        count = kb.count()
        return {
            "success": True,
            "ready": count > 0,
            "vector_count": count,
            "collection": "tongue_knowledge",
        }
    except Exception as e:
        return {"success": False, "ready": False, "vector_count": 0, "error": str(e)}


@router.post("/knowledge/search")
async def knowledge_search(data: dict):
    """检索知识库。"""
    query = (data.get("query") or "").strip()
    top_k = min(int(data.get("top_k", 5)), 20)
    if kb is None or not kb.ready():
        return {"success": False, "msg": "知识库未就绪", "items": [], "total": 0}
    if not query:
        return {"success": False, "msg": "查询内容不能为空", "items": [], "total": 0}
    try:
        result = kb.search_with_context(query, top_k=top_k)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "msg": str(e), "items": [], "total": 0}


@router.post("/knowledge/reindex")
async def knowledge_reindex():
    """重建知识库向量索引（从 chunk 文件重新嵌入）。"""
    if kb is None:
        return {"success": False, "msg": "知识库未初始化"}
    try:
        result = kb.reindex()
        return result
    except Exception as e:
        return {"success": False, "msg": str(e)}


@router.post("/knowledge/ingest")
async def knowledge_ingest(file_path: str = "", chunk_size: int = 1800):
    """
    导入 Markdown 文档到知识库。
    - file_path: Markdown 文件绝对路径
    - chunk_size: 分块字符数
    """
    if not file_path or not os.path.exists(file_path):
        return {"success": False, "msg": f"文件不存在: {file_path}"}
    try:
        result = ingest_markdown(file_path, chunk_size=chunk_size)
        return result
    except Exception as e:
        return {"success": False, "msg": str(e)}


@router.get("/knowledge/chunks")
async def knowledge_chunks():
    """列出知识库 chunk 文件。"""
    chunks_dir = Path(__file__).resolve().parent.parent / "data" / "knowledge_chunks"
    if not chunks_dir.exists():
        return {"success": True, "chunks": [], "total": 0}
    files = sorted(chunks_dir.glob("chunk_*.json"))
    chunks = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            chunks.append({
                "id": data.get("id"),
                "section_title": data.get("section_title", ""),
                "char_count": data.get("char_count", 0),
                "source_file": data.get("source_file", ""),
            })
        except Exception:
            pass
    return {"success": True, "chunks": chunks, "total": len(chunks)}
