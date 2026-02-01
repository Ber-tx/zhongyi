import sys
import os
from pathlib import Path

# 确保项目根目录在 sys.path 中
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.visualizer import Visualizer

# 示例分数（0-100）按新维度顺序
scores = {
    "气血状态": 55,
    "体液滋润度": 25,
    "湿浊程度": 75,
    "脾胃状态": 40,
    "血脉通畅度": 65,
    "外邪影响": 85
}

img_data = Visualizer.generate_radar(scores, overall_confidence=0.72, interpretation='湿浊偏高，建议改善饮食及代谢')

# 将 data URL 解码并保存为文件以便人工查看
import base64, re
m = re.match(r"data:image/png;base64,(.+)", img_data)
if m:
    b = base64.b64decode(m.group(1))
    out = ROOT / 'test_radar.png'
    with open(out, 'wb') as f:
        f.write(b)
    print(f'WROTE {out}')
else:
    print('生成失败')
