from ultralytics import YOLO
from .image_processor import ImageProcessor
from .expert_engine import ExpertEngine
from .visualizer import Visualizer
import pandas as pd


class TongueAnalyzer:
    def __init__(self, model_path, config_path):
        self.model = YOLO(model_path)
        self.engine = ExpertEngine(config_path)

    def format_results(self, results):
        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    "en_name": self.model.names[int(box.cls[0])],
                    "score": float(box.conf[0])
                })
        return detections

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

        # 2. 推理 (YOLO)
        results = self.model(img)
        detections = self.format_results(results)

        # 3. 专家辨证 (模块B/C) - 现在返回 (conclusion, scores, meta)
        conclusion, scores, meta = self.engine.analyze_syndrome(detections)

        # 依据 meta.confidence 判断是否给出明确结论
        overall_conf = meta.get('confidence', 0.0)
        interpretation = None
        if overall_conf < self.engine.decision_threshold:
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