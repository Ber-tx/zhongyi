import cv2
import numpy as np


class ImageProcessor:
    @staticmethod
    def process(img_bytes):
        # 1. 转换字节流为 OpenCV 格式
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None, False, {}

        # 2. 亮度检测 (使用 NumPy)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)

        # 3. 模糊检测 (使用拉普拉斯算子)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

        # 判定标准：模糊度 > 50 且 亮度在合理区间
        is_valid = blur_score > 50 and 30 < brightness < 240

        return img, is_valid, {
            "brightness": round(float(brightness), 2),
            "blur": round(float(blur_score), 2)
        }