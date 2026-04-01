import pandas as pd
import numpy as np
import json


class ExpertEngine:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            # 加载您上传的 tongue_detection_types.json
            self.config = json.load(f).get('tongue_types', {})
        # 可配置阈值
        self.detection_threshold = 0.5  # 用于支持特征
        self.decision_threshold = 0.7   # 输出明确结论的最低置信度

    def analyze_syndrome(self, detections):
        # 1. 基础检查
        if not detections:
            return "未检测到显著特征", self._default_scores(), {"confidence": 0.0}

        df = pd.DataFrame(detections)
        # 计算整体置信度：取最大值
        overall_conf = float(df['score'].max())

        # 2. 分数计算逻辑 (保持您原有的 base 计算不变)
        base = np.array([20.0, 20.0, 20.0, 20.0, 90.0], dtype=float)
        rule_map = {
            "red tongue yellow fur thick greasy fur": np.array([50, 0, 10, 0, -20]),
            "black tongue coating": np.array([30, 20, 0, 30, -40]),
            "purple tongue coating": np.array([10, 0, 0, 60, -25]),
            "pale tongue": np.array([0, 50, 0, 0, -15])
        }
        for _, row in df.iterrows():
            name = row.get('en_name')
            sc = float(row.get('score', 0.0))
            if name in rule_map and sc > 0:
                base = base + rule_map[name] * sc

        # 映射到更具临床可解释性的舌象维度分数（5维）
        base = np.clip(base, 10, 95)
        b = base.tolist()
        mapped_values = [
            (b[0] * 0.75 + (100 - b[1]) * 0.1),      # 舌色偏红（热象）
            (b[1] * 0.8 + (100 - b[0]) * 0.1),       # 舌色偏淡（虚寒/气血不足）
            (b[2] * 0.75 + (100 - b[4]) * 0.1),      # 苔色黄腻/湿热痰浊
            (b[3] * 0.85 + b[0] * 0.05),             # 瘀血征象
            ((100 - b[4]) * 0.7 + b[1] * 0.1)        # 津液亏虚（干燥）
        ]
        mapped_values = [float(np.clip(v, 10, 95)) for v in mapped_values]
        radar_keys = ['舌色偏红指数', '舌色偏淡指数', '苔色黄腻指数', '瘀血征象指数', '津液亏虚指数']
        scores = {k: {'mean': float(round(v, 2)), 'std': 0.0} for k, v in zip(radar_keys, mapped_values)}

        # 3. 【核心改进】生成单一结论并去重
        if overall_conf < self.decision_threshold:
            conclusion = "检测置信度较低，建议改善光线重拍"
        else:
            # a. 找到分数最高的维度作为“体质”
            max_idx = np.argmax(mapped_values)
            primary_dimension = radar_keys[max_idx]

            # b. 体质映射表
            constitution_map = {
                '舌色偏红指数': '偏热象（可见阴虚内热或湿热倾向）',
                '舌色偏淡指数': '偏虚寒象（可见气血不足或阳气偏弱）',
                '苔色黄腻指数': '痰湿湿热倾向',
                '瘀血征象指数': '气滞血瘀倾向',
                '津液亏虚指数': '阴津偏亏倾向'
            }
            main_constitution = constitution_map.get(primary_dimension, "基本平衡")

            # c. 获取去重后的视觉特征描述 (解决截图中的重复问题)
            top_detections = df.sort_values(by='score', ascending=False).head(3)['en_name'].tolist()
            unique_desc = list(dict.fromkeys([self.config.get(t, {}).get('cn', t) for t in top_detections]))
            visual_features = "；".join(unique_desc)

            # 组合最终结论：体质 + 特征说明
            conclusion = f"分析提示【{main_constitution}】。特征识别：{visual_features}"

        return conclusion, scores, {"confidence": overall_conf}

    def _calculate_scores(self, tags):
        # 保留原有按标签计算的便捷方法（仍用于某些情况）
        base = np.array([20.0, 20.0, 20.0, 20.0, 90.0])
        if "red tongue yellow fur thick greasy fur" in tags:
            base += np.array([50, 0, 10, 0, -20])
        if "black tongue coating" in tags:
            base += np.array([30, 20, 0, 30, -40])
        if "purple tongue coating" in tags:
            base += np.array([10, 0, 0, 60, -25])
        if "pale tongue" in tags:
            base += np.array([0, 50, 0, 0, -15])
        base = np.clip(base, 10, 95)
        keys = ['湿热', '气虚', '阴虚', '血瘀', '健康度']
        return dict(zip(keys, base.tolist()))

    def _default_scores(self):
        # 返回与新格式兼容的默认 mean/std
        return {
            '舌色偏红指数': {'mean': 20.0, 'std': 0.0},
            '舌色偏淡指数': {'mean': 20.0, 'std': 0.0},
            '苔色黄腻指数': {'mean': 20.0, 'std': 0.0},
            '瘀血征象指数': {'mean': 20.0, 'std': 0.0},
            '津液亏虚指数': {'mean': 20.0, 'std': 0.0}
        }