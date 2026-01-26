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
                "main_result": "图像质量不佳（过暗或模糊），请在光线充足处重新拍摄"
            }

        # 2. 推理 (YOLO)
        results = self.model(img)
        detections = self.format_results(results)

        # 3. 专家辨证 (模块B/C)
        conclusion, scores = self.engine.analyze_syndrome(detections)

        # 4. 可视化 (模块D)
        radar_img = Visualizer.generate_radar(scores)

        return {
            "success": True,
            "main_result": conclusion,
            "chart_img": radar_img,
            "data_depth": {
                "scores": scores,
                "quality": quality,
                "feature_count": len(detections)
            }
        }