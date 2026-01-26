import matplotlib

matplotlib.use('Agg')  # 关键：防止在无显示器的服务器环境报错
import matplotlib.pyplot as plt
import numpy as np
import io, base64

# 设置中文支持
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class Visualizer:
    @staticmethod
    def generate_radar(scores_dict):
        labels = list(scores_dict.keys())
        values = list(scores_dict.values())

        # 雷达图首尾闭合
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        ax.fill(angles, values, color='#ff4d4f', alpha=0.3)
        ax.plot(angles, values, color='#ff4d4f', linewidth=2)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=12)
        ax.set_yticklabels([])  # 隐藏刻度数字

        plt.title('中医体质多维分析图谱', y=1.1, fontsize=15)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)  # 必须显式释放内存
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()