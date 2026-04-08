from .image_processor import ImageProcessor
from .visualizer import Visualizer
import base64
import json
import os
import re

import cv2
import httpx
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class TongueAnalyzer:
    def __init__(self, model_path=None, config_path=None):
        # 兼容旧初始化参数，避免改动路由层调用。
        self.model_path = model_path
        self.config_path = config_path
        self.decision_threshold = 0.7

        bypass_raw = os.getenv("QWEN_BYPASS_PROXY", os.getenv("DEEPSEEK_BYPASS_PROXY", "1"))
        bypass_proxy = str(bypass_raw).strip().lower() in {"1", "true", "yes", "on"}
        timeout_sec = float(os.getenv("QWEN_TIMEOUT", os.getenv("DEEPSEEK_TIMEOUT", "30")))
        api_key = os.getenv("QWEN_API_KEY", os.getenv("DEEPSEEK_API_KEY"))
        base_url = os.getenv(
            "QWEN_BASE_URL",
            os.getenv("DEEPSEEK_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        )

        http_client = httpx.Client(timeout=timeout_sec, trust_env=not bypass_proxy)
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout_sec,
            max_retries=1,
            http_client=http_client,
        )
        self.model_name = os.getenv(
            "QWEN_VISION_MODEL",
            os.getenv("DEEPSEEK_VISION_MODEL", "qwen-vl-plus"),
        )
        self.score_keys = [
            "舌色偏红指数",
            "舌色偏淡指数",
            "苔色黄腻指数",
            "瘀血征象指数",
            "津液亏虚指数",
        ]

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

    def _analyze_by_llm(self, img):
        ok, buffer = cv2.imencode('.jpg', img)
        if not ok:
            raise ValueError("图像编码失败")

        b64_img = base64.b64encode(buffer.tobytes()).decode("utf-8")

        # 1. 细化维度定义，让 AI 打分有据可依
        dimension_desc = (
            "- 舌色偏红指数: 0(淡白)-50(淡红)-100(红绛/紫红)\n"
            "- 舌色偏淡指数: 0(红润)-100(极度淡白/枯白)\n"
            "- 苔色黄腻指数: 0(薄白)-100(深黄、厚腻)\n"
            "- 瘀血征象指数: 0(无)-100(明显紫斑、瘀点、舌下静脉怒张)\n"
            "- 津液亏虚指数: 0(润泽)-100(干燥、燥裂、无苔)"
        )

        # 2. 结构化 Prompt
        prompt = (
            "## 角色\n"
            "你是一位深耕中医诊断学20年的舌诊专家。请对提供的舌象图进行客观、严谨的分析。\n\n"
            "## 任务要求\n"
            "1. **视觉观察**：仔细辨识舌质颜色、舌体形状（胖瘦/齿痕）、苔质厚薄、苔色深浅及干湿度。\n"
            "2. **分值评估**：基于以下标准进行打分（0-100）：\n"
            f"{dimension_desc}\n"
            "3. **综合辨证**：结合上述特征，给出病机分析及调护建议。\n\n"
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

        # 建议：如果模型支持，开启 json_mode
        # 这里保持你的 OpenAI 调用结构
        resp = self.client.chat.completions.create(
            model=self.model_name,
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
            temperature=0.1,  # 降低随机性，提高诊断的一致性
            max_tokens=1000,
            # response_format={"type": "json_object"} # 如果使用 qwen-vl-max 等支持 JSON Mode 的模型可开启
        )

        content = resp.choices[0].message.content if resp.choices else ""
        # 调试用：print(f"LLM Raw Output: {content}")

        payload = self._extract_json(content)
        # ... 后面保持原有的逻辑不变 ...

        main_result = str(payload.get("main_result", "")).strip()
        if not main_result:
            raise ValueError("main_result 为空")

        confidence = float(payload.get("confidence", 0.0))
        confidence = max(0.0, min(1.0, confidence))

        scores = self._normalize_scores(payload.get("scores", {}))
        return main_result, confidence, scores

    def analyze(self, img_bytes):
        # 1. 预处理 (模块A)
        img, is_valid, quality = ImageProcessor.process(img_bytes)
        if not is_valid:
            return {
                "success": False,
                "msg": "图像质量不佳（过暗或模糊），请在光线充足处重新拍摄",
                "data": {
                    "main_result": "图像质量不佳（过暗或模糊），请在光线充足处重新拍摄"
                }
            }

        # 2. 推理 (Qwen/兼容 OpenAI 视觉模型)
        try:
            conclusion, overall_conf, scores = self._analyze_by_llm(img)
        except Exception as e:
            err_text = str(e)
            if "Connection error" in err_text or "Proxy" in err_text or "10054" in err_text:
                err_text = "网络连接失败（疑似代理拦截），请检查网络或设置 QWEN_BYPASS_PROXY=1"
            elif "unknown variant `image_url`" in err_text or "invalid_request_error" in err_text:
                err_text = "当前模型不支持图片输入。请确认使用视觉模型并设置 QWEN_VISION_MODEL（示例: qwen-vl-plus）"
            return {
                "success": False,
                "msg": f"大模型分析失败: {err_text}",
                "data": {
                    "main_result": "大模型分析失败，请稍后重试"
                }
            }

        # 3. 置信度解释 + 可视化
        interpretation = None
        if overall_conf < self.decision_threshold:
            interpretation = '本次分析置信度不足，建议重新拍摄或上传多张舌象以提高可信度。'

        # 4. 可视化 (模块D) - 将 interpretation 与置信度传入
        radar_img = Visualizer.generate_radar(scores,
                                             interpretation=interpretation,
                                             overall_confidence=overall_conf)

        return {
            "success": True,
            "data": {
                "main_result": conclusion,
                "chart_img": radar_img,
                "confidence": overall_conf,
                "scores": scores
            }
        }