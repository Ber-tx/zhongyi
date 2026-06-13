"""
YOLOv8 舌象检测服务
适配自项目2的 YOLOService，集成到项目1的 tcm-ai-service 中。
"""

import math
import cv2
import numpy as np
from ultralytics import YOLO
from typing import Any, Dict, List
from datetime import datetime


TONGUE_CLASSES = {
    0: {"code": "jiankangshe", "label": "健康舌"},
    1: {"code": "botaishe", "label": "薄苔舌"},
    2: {"code": "hongshe", "label": "红舌"},
    3: {"code": "zishe", "label": "紫舌"},
    4: {"code": "pangdashe", "label": "胖大舌"},
    5: {"code": "shoushe", "label": "瘦舌"},
    6: {"code": "hongdianshe", "label": "红点舌"},
    7: {"code": "liewenshe", "label": "裂纹舌"},
    8: {"code": "chihenshe", "label": "齿痕舌"},
    9: {"code": "baitaishe", "label": "白苔舌"},
    10: {"code": "huangtaishe", "label": "黄苔舌"},
    11: {"code": "heitaishe", "label": "黑苔舌"},
    12: {"code": "huataishe", "label": "花苔舌"},
    13: {"code": "shenquao", "label": "肾阙凹"},
    14: {"code": "shenqutu", "label": "肾阙凸"},
    15: {"code": "gandanao", "label": "肝胆凹"},
    16: {"code": "gandantu", "label": "肝胆凸"},
    17: {"code": "piweiao", "label": "脾胃凹"},
    18: {"code": "xinfeitu", "label": "心肺凸"},
    19: {"code": "xinfeiao", "label": "心肺凹"},
}

BOX_COLORS = [
    "#40C4FF", "#D7FF36", "#FF7043", "#7E57C2", "#1E3A8A",
    "#26A69A", "#FFCA28", "#D500F9", "#00E676", "#EC407A",
    "#AB47BC", "#8D6E63", "#78909C", "#66BB6A", "#FFA726",
    "#29B6F6", "#FF5252", "#5C6BC0", "#00ACC1", "#FDD835",
]


class YOLODetector:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)

    def detect(self, image_path: str) -> Dict[str, Any]:
        """对单张图片执行 YOLO 检测。"""
        results = self.model(image_path)
        img = cv2.imread(image_path)
        shape = img.shape if img is not None else None
        return self._build_result(results, shape)

    def detect_array(self, img: np.ndarray) -> Dict[str, Any]:
        """对 numpy 数组执行检测。"""
        results = self.model(img)
        return self._build_result(results, img.shape)

    def multi_detect(self, image_paths: List[str], min_appear_rate: float = 0.6) -> Dict[str, Any]:
        """多帧检测 + 聚合。"""
        results = [self.detect(p) for p in image_paths]
        return self._aggregate(results, min_appear_rate)

    def _build_result(self, results, img_shape=None):
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    cls = int(box.cls[0].cpu().numpy())
                    info = TONGUE_CLASSES.get(cls, {"code": "unknown", "label": "未知"})
                    detections.append({
                        "class_id": cls,
                        "class_code": info["code"],
                        "class": info["label"],
                        "confidence": round(float(conf), 3),
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "color": BOX_COLORS[cls % len(BOX_COLORS)],
                    })

        area_info = {"area": 0, "coverage": 0, "bbox": [0, 0, 0, 0]}
        if detections and img_shape:
            largest = max(detections, key=lambda d: (d["bbox"][2] - d["bbox"][0]) * (d["bbox"][3] - d["bbox"][1]))
            b = largest["bbox"]
            w_img, h_img = img_shape[1], img_shape[0]
            area = (b[2] - b[0]) * (b[3] - b[1])
            coverage = round(area / (w_img * h_img) * 100, 2)
            area_info = {"area": int(area), "coverage": coverage, "bbox": b}

        shape_out = {"width": 0, "height": 0}
        if img_shape is not None:
            shape_out = {"width": int(img_shape[1]), "height": int(img_shape[0])}

        return {
            "detections": detections,
            "image_shape": shape_out,
            "tongue_area": area_info,
            "timestamp": datetime.now().isoformat(),
        }

    def _aggregate(self, all_results: List[Dict[str, Any]], min_appear_rate: float = 0.6) -> Dict[str, Any]:
        """多帧聚合：同一类出现在 ≥min_appear_rate 帧中则保留，置信度取平均。"""
        if not all_results:
            return {"detections": [], "image_shape": {}, "tongue_area": {}, "timestamp": ""}

        total_frames = len(all_results)
        threshold = math.ceil(total_frames * min_appear_rate)

        class_counts: Dict[int, int] = {}
        class_confs: Dict[int, List[float]] = {}
        class_bboxes: Dict[int, List[list]] = {}
        class_meta: Dict[int, dict] = {}
        seen_per_frame: List[set] = [set() for _ in range(total_frames)]

        for fi, frame_result in enumerate(all_results):
            for det in frame_result.get("detections", []):
                cid = det["class_id"]
                if cid in seen_per_frame[fi]:
                    continue
                seen_per_frame[fi].add(cid)

                class_counts[cid] = class_counts.get(cid, 0) + 1
                class_confs.setdefault(cid, []).append(det["confidence"])
                class_bboxes.setdefault(cid, []).append(det["bbox"])
                if cid not in class_meta:
                    class_meta[cid] = {
                        "class": det["class"],
                        "class_code": det["class_code"],
                        "color": det["color"],
                    }

        detections = []
        for cid, count in class_counts.items():
            if count < threshold:
                continue
            meta = class_meta[cid]
            avg_conf = round(sum(class_confs[cid]) / len(class_confs[cid]), 3)
            best_idx = int(np.argmax(class_confs[cid]))
            bbox = class_bboxes[cid][best_idx]
            detections.append({
                "class_id": cid,
                "class_code": meta["class_code"],
                "class": meta["class"],
                "confidence": avg_conf,
                "bbox": bbox,
                "color": meta["color"],
            })

        last = all_results[-1]
        return {
            "detections": detections,
            "image_shape": last.get("image_shape", {}),
            "tongue_area": last.get("tongue_area", {}),
            "timestamp": self._now(),
        }

    @staticmethod
    def _now():
        return datetime.now().isoformat()
