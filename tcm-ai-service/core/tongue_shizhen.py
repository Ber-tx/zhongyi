"""
舌诊分析引擎 v2.0
双引擎架构：
  1. YOLOv8 目标检测（主引擎）— 快速、本地、无网络依赖
  2. Qwen 视觉大模型复诊（副引擎）— 深度分析、保留原"大模型复诊"能力

YOLO 检测结果映射为 5 维度量化评分 + 雷达图可视化。
"""

import base64
import json
import os
import re
import logging
from pathlib import Path

import cv2
import httpx
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

from .image_processor import ImageProcessor
from .visualizer import Visualizer

logger = logging.getLogger(__name__)

load_dotenv()

# ── 项目路径 ────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
DEFAULT_YOLO_PATH = str(MODEL_DIR / "best.pt")
DEFAULT_ANNOTATION_PATH = str(MODEL_DIR / "舌象标注规范表.xlsx")

# ── YOLO → 5 维度评分映射表 ──────────────────────────────
# 每条规则: (class_id, 置信度系数, {维度名: 得分贡献})
# class_id 为 -1 表示"任意匹配到的所有 class 的聚合"
SCORE_MAP = {
    # 舌色偏红 —— 红舌、红点舌贡献大
    "舌色偏红指数": {
        2: 0.45,    # 红舌
        6: 0.25,    # 红点舌
        3: 0.15,    # 紫舌（红绛）
    },
    # 舌色偏淡 —— 白苔舌、薄苔舌、健康舌反向
    "舌色偏淡指数": {
        9: 0.50,    # 白苔舌
        1: 0.30,    # 薄苔舌
        0: -0.30,   # 健康舌（反向抑制）
    },
    # 苔色黄腻 —— 黄苔舌
    "苔色黄腻指数": {
        10: 0.70,   # 黄苔舌
        12: 0.10,   # 花苔舌
    },
    # 瘀血征象 —— 紫舌、红点舌
    "瘀血征象指数": {
        3: 0.55,    # 紫舌
        6: 0.25,    # 红点舌
        11: 0.10,   # 黑苔舌
    },
    # 津液亏虚 —— 裂纹舌、瘦舌
    "津液亏虚指数": {
        7: 0.55,    # 裂纹舌
        5: 0.20,    # 瘦舌
        12: 0.10,   # 花苔舌
    },
}

# 基准默认分（未匹配到任何阳性特征时的基线）
BASE_SCORES = {
    "舌色偏红指数": 25,
    "舌色偏淡指数": 15,
    "苔色黄腻指数": 10,
    "瘀血征象指数": 10,
    "津液亏虚指数": 10,
}


class TongueAnalyzer:
    def __init__(self, model_path=None, config_path=None):
        self.model_path = model_path or DEFAULT_YOLO_PATH
        self.config_path = config_path
        self.decision_threshold = 0.7

        # ── YOLO 引擎（懒加载） ──
        self._yolo = None
        self._annotator = None

        # ── LLM 引擎（大模型复诊，懒加载） ──
        self._llm_config = {
            "api_key": os.getenv("QWEN_API_KEY", os.getenv("DEEPSEEK_API_KEY")),
            "base_url": os.getenv(
                "QWEN_BASE_URL",
                os.getenv("DEEPSEEK_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            ),
            "timeout": float(os.getenv("QWEN_TIMEOUT", os.getenv("DEEPSEEK_TIMEOUT", "30"))),
            "bypass_proxy": os.getenv("QWEN_BYPASS_PROXY", os.getenv("DEEPSEEK_BYPASS_PROXY", "1")).strip().lower() in {"1", "true", "yes", "on"},
            "model": os.getenv("QWEN_VISION_MODEL", os.getenv("DEEPSEEK_VISION_MODEL", "qwen-vl-plus")),
        }
        self._client = None
        self.score_keys = [
            "舌色偏红指数",
            "舌色偏淡指数",
            "苔色黄腻指数",
            "瘀血征象指数",
            "津液亏虚指数",
        ]

    @property
    def yolo(self):
        if self._yolo is None:
            from .yolo_detector import YOLODetector
            self._yolo = YOLODetector(self.model_path)
        return self._yolo

    @property
    def annotator(self):
        if self._annotator is None:
            from .annotation_matcher import AnnotationMatcher
            self._annotator = AnnotationMatcher(DEFAULT_ANNOTATION_PATH)
        return self._annotator

    def _get_llm_client(self):
        if self._client is None:
            cfg = self._llm_config
            if not cfg["api_key"]:
                self._client = None
                return None
            http_client = httpx.Client(timeout=cfg["timeout"], trust_env=not cfg["bypass_proxy"])
            self._client = OpenAI(
                api_key=cfg["api_key"],
                base_url=cfg["base_url"],
                timeout=cfg["timeout"],
                max_retries=1,
                http_client=http_client,
            )
        return self._client

    # ── YOLO 检测 → 5 维度评分 ──────────────────────────────────

    def _yolo_to_scores(self, detections: list) -> dict:
        """将 YOLO 检测结果映射为 5 维度量化评分。"""
        scores = dict(BASE_SCORES)

        # 按 class_id 聚合最高置信度
        class_max_conf = {}
        for d in detections:
            cid = d["class_id"]
            conf = d["confidence"]
            if cid not in class_max_conf or conf > class_max_conf[cid]:
                class_max_conf[cid] = conf

        for dim_name, class_weights in SCORE_MAP.items():
            boost = 0.0
            for cid, weight in class_weights.items():
                conf = class_max_conf.get(cid)
                if conf is not None:
                    boost += weight * conf
            scores[dim_name] = max(0.0, min(100.0, scores[dim_name] + boost * 100))

        # 若有"健康舌"且置信度高 → 各病理分降低
        healthy_conf = class_max_conf.get(0)
        if healthy_conf and healthy_conf > 0.6:
            factor = 1.0 - (healthy_conf - 0.6) / 0.4 * 0.5  # 0.5 ~ 1.0 缩放
            for k in scores:
                if k != "舌色偏淡指数":
                    scores[k] = max(0.0, scores[k] * factor)

        return {k: {"mean": round(v, 2), "std": round(max(5, 25 - v * 0.15), 2)} for k, v in scores.items()}

    def _yolo_confidence(self, detections: list) -> float:
        """基于检测框数量与平均置信度计算整体置信度。"""
        if not detections:
            return 0.0
        avg_conf = np.mean([d["confidence"] for d in detections])
        count_boost = min(1.0, len(detections) / 3.0) * 0.1
        return min(0.95, avg_conf + count_boost)

    def _yolo_main_result(self, detections: list, match_result: dict) -> str:
        """从 YOLO 检测结果生成主结论文本。"""
        if not detections:
            return "未检测到明确舌象区域，请重新拍摄清晰的舌面照片。"

        labels = [d["class"] for d in detections]
        confs = [f"{d['confidence']:.0%}" for d in detections]
        label_str = "、".join(f"{l}({c})" for l, c in zip(labels, confs))

        # 从标注表获取解释
        explanations = []
        for item in match_result.get("items", []):
            diag = item.get("中医诊断") or item.get("diagnosis") or ""
            if diag:
                explanations.append(diag)

        lines = [f"YOLOv8 舌象检测识别到 {label_str}。"]
        if explanations:
            lines.append("；".join(explanations[:3]))
        lines.append("建议结合视觉大模型复诊结果综合判断。")
        return "".join(lines)

    # ── LLM 复诊（保留原大模型能力） ──────────────────────────

    def _extract_json(self, text):
        text = (text or "").strip()
        if not text:
            raise ValueError("大模型返回为空")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        block = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", text)
        if block:
            return json.loads(block.group(1))
        first = text.find("{")
        last = text.rfind("}")
        if first >= 0 and last > first:
            return json.loads(text[first:last + 1])
        raise ValueError("无法从大模型返回中解析 JSON")

    def _normalize_scores(self, scores_raw):
        if not isinstance(scores_raw, dict):
            raise ValueError("scores 格式错误")
        scores = {}
        for key in self.score_keys:
            value = scores_raw.get(key, 20)
            if isinstance(value, dict):
                mean = float(value.get("mean", 20.0))
                std = float(value.get("std", 0.0))
            else:
                mean = float(value)
                std = 0.0
            mean = max(0.0, min(100.0, mean))
            std = max(0.0, min(30.0, std))
            scores[key] = {"mean": round(mean, 2), "std": round(std, 2)}
        return scores

    def _review_by_llm(self, img: np.ndarray, yolo_result: dict = None) -> dict:
        """
        大模型复诊：Qwen 视觉模型对舌象进行深度分析。
        """
        llm_client = self._get_llm_client()
        if llm_client is None:
            raise ValueError("未配置大模型 API Key（QWEN_API_KEY），无法进行复诊")

        ok, buffer = cv2.imencode('.jpg', img)
        if not ok:
            raise ValueError("图像编码失败")
        b64_img = base64.b64encode(buffer.tobytes()).decode("utf-8")

        yolo_context = ""
        if yolo_result and yolo_result.get("detections"):
            dets = yolo_result["detections"]
            yolo_context = "\n\n## YOLOv8 初步检测结果（供参考）\n"
            for d in dets:
                yolo_context += f"- {d['class']} (置信度: {d['confidence']:.0%})\n"

        dimension_desc = (
            "- 舌色偏红指数: 0(淡白)-50(淡红)-100(红绛/紫红)\n"
            "- 舌色偏淡指数: 0(红润)-100(极度淡白/枯白)\n"
            "- 苔色黄腻指数: 0(薄白)-100(深黄、厚腻)\n"
            "- 瘀血征象指数: 0(无)-100(明显紫斑、瘀点、舌下静脉怒张)\n"
            "- 津液亏虚指数: 0(润泽)-100(干燥、燥裂、无苔)"
        )

        prompt = (
            "## 角色\n"
            "你是一位深耕中医诊断学20年的舌诊专家。请对提供的舌象图进行客观、严谨的分析。\n\n"
            "## 任务要求\n"
            "1. **视觉观察**：仔细辨识舌质颜色、舌体形状（胖瘦/齿痕）、苔质厚薄、苔色深浅及干湿度。\n"
            "2. **分值评估**：基于以下标准进行打分（0-100）：\n"
            f"{dimension_desc}\n"
            "3. **综合辨证**：结合上述特征，给出病机分析及调护建议。\n"
            f"{yolo_context}\n"
            "## 输出格式（严格 JSON）\n"
            "必须输出纯 JSON，严禁任何 markdown 代码块标识或解释文字。\n"
            "{\n"
            '  "main_result": "指出核心证候（如脾虚湿盛、阴虚火旺等），描述舌象依据（如舌淡苔白、边有齿痕），并给出2条饮食建议。字数100-150字。",\n'
            '  "confidence": 0.0-1.0 之间的视觉识别可信度,\n'
            '  "scores": {\n'
            '    "舌色偏红指数": int,\n'
            '    "舌色偏淡指数": int,\n'
            '    "苔色黄腻指数": int,\n'
            '    "瘀血征象指数": int,\n'
            '    "津液亏虚指数": int\n'
            '  }\n'
            "}"
        )

        resp = llm_client.chat.completions.create(
            model=self._llm_config["model"],
            messages=[
                {
                    "role": "system",
                    "content": "你是一个只输出 JSON 格式数据的专业中医诊断系统。不要进行任何对话，直接返回数据结构。"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_img}", "detail": "high"},
                        },
                    ],
                }
            ],
            temperature=0.1,
            max_tokens=1000,
        )

        content = resp.choices[0].message.content if resp.choices else ""
        payload = self._extract_json(content)
        main_result = str(payload.get("main_result", "")).strip()
        if not main_result:
            raise ValueError("main_result 为空")
        confidence = max(0.0, min(1.0, float(payload.get("confidence", 0.0))))
        scores = self._normalize_scores(payload.get("scores", {}))
        return main_result, confidence, scores

    # ── 主入口 ──────────────────────────────────────────────

    def analyze(self, img_bytes: bytes, use_llm_review: bool = True) -> dict:
        """
        舌诊分析主入口。

        流程：
          1. 图像质量检查
          2. YOLOv8 检测（主引擎）
          3. 标注匹配
          4. YOLO → 5 维度评分映射 + 雷达图
          5. （可选）Qwen 视觉大模型复诊
          6. 合并结果返回

        Args:
            img_bytes: 原始图片字节
            use_llm_review: 是否使用大模型复诊（默认 True）

        Returns:
            与前端兼容的响应字典
        """
        # 1. 图像质量检查
        img, is_valid, quality = ImageProcessor.process(img_bytes)
        if not is_valid:
            return {
                "success": False,
                "msg": "图像质量不佳（过暗或模糊），请在光线充足处重新拍摄",
                "data": {
                    "main_result": "图像质量不佳（过暗或模糊），请在光线充足处重新拍摄"
                }
            }

        # 2. 保存临时文件供 YOLO 检测
        tmp_path = None
        try:
            tmp_path = str(MODEL_DIR / "_tmp_tongue.jpg")
            cv2.imwrite(tmp_path, img)

            # 3. YOLO 检测
            yolo_result = self.yolo.detect(tmp_path)
            detections = yolo_result.get("detections", [])

            # 4. 标注匹配
            match_result = self.annotator.match_detections(detections)

            # 5. YOLO → 5 维度评分
            yolo_scores = self._yolo_to_scores(detections)
            yolo_conf = self._yolo_confidence(detections)
            yolo_main = self._yolo_main_result(detections, match_result)

            # 6. （可选）大模型复诊
            llm_review_result = None
            if use_llm_review and yolo_conf > 0.3:
                try:
                    llm_main, llm_conf, llm_scores = self._review_by_llm(img, yolo_result)
                    llm_review_result = {
                        "main_result": llm_main,
                        "confidence": llm_conf,
                        "scores": llm_scores,
                    }
                except Exception as e:
                    logger.warning(f"大模型复诊失败（不影响主结果）: {e}")

            # 7. 确定最终输出
            if llm_review_result:
                final_main = llm_review_result["main_result"]
                final_conf = llm_review_result["confidence"]
                # 混合评分：YOLO + LLM 加权平均
                final_scores = {}
                for key in self.score_keys:
                    yolo_val = yolo_scores.get(key, {}).get("mean", 20)
                    llm_val = llm_review_result["scores"].get(key, {}).get("mean", 20)
                    # YOLO 权重 0.3, LLM 权重 0.7
                    blended = round(yolo_val * 0.3 + llm_val * 0.7, 2)
                    std_val = round(abs(yolo_val - llm_val) * 0.3 + 5, 2)
                    final_scores[key] = {"mean": blended, "std": min(30.0, std_val)}
                final_confidence = max(yolo_conf, llm_conf)
            else:
                final_main = yolo_main
                final_conf = yolo_conf
                final_scores = yolo_scores

            # 8. 置信度解释 + 可视化
            interpretation = None
            if final_conf < self.decision_threshold:
                interpretation = "本次分析置信度不足，建议重新拍摄或上传多张舌象以提高可信度。"

            radar_img = Visualizer.generate_radar(
                final_scores,
                interpretation=interpretation,
                overall_confidence=final_conf,
            )

            # 9. 构建返回
            response_data = {
                "success": True,
                "data": {
                    "main_result": final_main,
                    "chart_img": radar_img,
                    "confidence": final_conf,
                    "scores": final_scores,
                    "yolo_detections": detections,
                    "annotation_match": match_result,
                    "image_shape": yolo_result.get("image_shape", {}),
                    "tongue_area": yolo_result.get("tongue_area", {}),
                },
            }

            # 附加 llm review 详情
            if llm_review_result:
                response_data["data"]["llm_review"] = {
                    "confidence": llm_review_result["confidence"],
                }

            return response_data

        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
