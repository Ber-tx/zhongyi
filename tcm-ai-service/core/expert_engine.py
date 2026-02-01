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
        # detections: list of {'en_name': str, 'score': float}
        if not detections:
            return "未检测到显著特征", self._default_scores(), {"per_detection": [], "confidence": 0.0}

        df = pd.DataFrame(detections)
        if df.empty or 'score' not in df.columns:
            return "图像特征不清晰", self._default_scores(), {"per_detection": detections, "confidence": 0.0}

        df['score'] = df['score'].astype(float)

        # 支持的高置信特征（用于结论说明）
        supporting = df[df['score'] >= self.detection_threshold].to_dict(orient='records')

        if df.empty:
            return "图像特征不清晰", self._default_scores(), {"per_detection": detections, "confidence": 0.0}

        # 计算五维得分，使用检测置信度加权
        base = np.array([20.0, 20.0, 20.0, 20.0, 90.0], dtype=float)

        # 定义规则映射（可在配置中扩展）
        rule_map = {
            "red tongue yellow fur thick greasy fur": np.array([50, 0, 10, 0, -20]),
            "black tongue coating": np.array([30, 20, 0, 30, -40]),
            "purple tongue coating": np.array([10, 0, 0, 60, -25]),
            "pale tongue": np.array([0, 50, 0, 0, -15])
        }

        # 对每个检测按置信度加权贡献
        for _, row in df.iterrows():
            name = row.get('en_name')
            sc = float(row.get('score', 0.0))
            if name in rule_map and sc > 0:
                base = base + rule_map[name] * sc

        # 将分数约束到合理范围（这里我们生成 6 维用于前端雷达图）
        # 目标维度（与可视化一致）
        radar_keys = ['气血状态', '体液滋润度', '湿浊程度', '脾胃状态', '血脉通畅度', '外邪影响']

        # 为兼容原有规则，定义一个简单映射，将先前的 5 维 base 映射到新的 6 维影响上。
        # 这里保持原有结论逻辑不变，仅用于前端可视化输出的转换。
        # 将原 base(5) 映射到 6 维：湿热->气血状态/湿浊程度，气虚->体液滋润度/脾胃，阴虚->体液/气血，血瘀->血脉通畅度，健康度->外邪影响(反向)
        base = np.clip(base, 10, 95)
        b = base.tolist()
        mapped = [
            (b[0] * 0.6 + b[3] * 0.1 + b[2] * 0.1),  # 气血状态（受湿热、血瘀、阴虚影响）
            (b[1] * 0.2 + b[2] * 0.5),               # 体液滋润度（气虚/阴虚为主）
            (b[0] * 0.6 + b[2] * 0.2),               # 湿浊程度（湿热/阴虚）
            (b[1] * 0.5 + b[4] * 0.1),               # 脾胃状态（气虚/健康度弱影响）
            (b[3] * 0.8 + b[0] * 0.1),               # 血脉通畅度（血瘀/湿热）
            (100 - b[4]) * 0.6 + b[0] * 0.1          # 外邪影响（与健康度、湿热有负相关/正相关混合）
        ]

        # 生成 mean/std 格式（单次推理 std=0）
        scores = {k: {'mean': float(round(v, 2)), 'std': 0.0} for k, v in zip(radar_keys, mapped)}

        # 计算整体置信度：取检测置信度的最大值为整体置信度（也可改为平均）
        overall_conf = float(df['score'].max())

        # 生成结论：综合多个高置信度特征而非仅 top1
        if overall_conf < self.decision_threshold:
            conclusion = "本次分析置信度不足，建议重新拍摄以获得更可靠结果"
        else:
            topk = df.sort_values(by='score', ascending=False).head(3)['en_name'].tolist()
            # 组合 topk 的中文描述（若配置中存在）
            cn_texts = [self.config.get(t, {}).get('cn', t) for t in topk]
            conclusion = '；'.join(cn_texts)

        meta = {
            'per_detection': detections,
            'supporting': supporting,
            'confidence': overall_conf
        }

        return conclusion, scores, meta

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
            '气血状态': {'mean': 20.0, 'std': 0.0},
            '体液滋润度': {'mean': 20.0, 'std': 0.0},
            '湿浊程度': {'mean': 20.0, 'std': 0.0},
            '脾胃状态': {'mean': 20.0, 'std': 0.0},
            '血脉通畅度': {'mean': 20.0, 'std': 0.0},
            '外邪影响': {'mean': 10.0, 'std': 0.0}
        }