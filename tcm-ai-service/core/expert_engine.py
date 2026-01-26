import pandas as pd
import numpy as np
import json


class ExpertEngine:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            # 加载您上传的 tongue_detection_types.json
            self.config = json.load(f).get('tongue_types', {})

    def analyze_syndrome(self, detections):
        if not detections:
            return "未检测到显著特征", self._default_scores()

        # 1. 数据清洗：利用 Pandas 过滤低置信度数据
        df = pd.DataFrame(detections)
        df = df[df['score'] > 0.5]

        if df.empty:
            return "图像特征不清晰", self._default_scores()

        # 2. 计算五维得分 (湿热, 气虚, 阴虚, 血瘀, 健康度)
        tags = set(df['en_name'].tolist())
        scores = self._calculate_scores(tags)

        # 3. 提取结论文本 (取置信度最高的一个特征)
        top_tag = df.sort_values(by='score', ascending=False).iloc[0]['en_name']
        conclusion = self.config.get(top_tag, {}).get('cn', f"检测到{top_tag}")

        return conclusion, scores

    def _calculate_scores(self, tags):
        # 初始化基础分
        base = np.array([20.0, 20.0, 20.0, 20.0, 90.0])

        # 模拟专家辨证逻辑
        if "red tongue yellow fur thick greasy fur" in tags:
            base += np.array([50, 0, 10, 0, -20])
        if "black tongue coating" in tags:
            base += np.array([30, 20, 0, 30, -40])
        if "purple tongue coating" in tags:
            base += np.array([10, 0, 0, 60, -25])
        if "pale tongue" in tags:
            base += np.array([0, 50, 0, 0, -15])

        # 限制分数范围在 10-95
        base = np.clip(base, 10, 95)
        keys = ['湿热', '气虚', '阴虚', '血瘀', '健康度']
        return dict(zip(keys, base.tolist()))

    def _default_scores(self):
        return {'湿热': 20, '气虚': 20, '阴虚': 20, '血瘀': 20, '健康度': 90}