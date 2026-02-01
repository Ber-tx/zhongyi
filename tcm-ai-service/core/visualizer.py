import matplotlib

import matplotlib

matplotlib.use('Agg')  # 防止在无显示器的服务器环境报错
import matplotlib.pyplot as plt
import numpy as np
import io, base64
from matplotlib import rc_context


class Visualizer:
    @staticmethod
    def generate_radar(scores_dict,
                       interpretation: str = None,
                       overall_confidence: float = None,
                       size=(7, 7),
                       dpi=100,
                       max_scale=100,
                       annotate=True):
        """生成带有刻度、分区背景和简短文字解读的雷达图。

        支持两种 `scores_dict` 格式：
        - {dim: number}
        - {dim: {'mean': number, 'std': number}}

        返回 data URL (png)
        """
        if not isinstance(scores_dict, dict) or len(scores_dict) == 0:
            raise ValueError('scores_dict must be a non-empty dict')

        # 预设维度（顺序固定）和次级描述
        dims = [
            ("气血状态", "舌质颜色/饱和度"),
            ("体液滋润度", "表面反光率/干燥度"),
            ("湿浊程度", "舌苔厚度/腐腻感"),
            ("脾胃状态", "舌体轮廓/齿痕算法"),
            ("血脉通畅度", "斑点/脉络/紫色分量"),
            ("外邪影响", "苔色/色温偏向")
        ]
        labels = [d[0] for d in dims]

        means = []
        stds = []
        for lab in labels:
            v = scores_dict.get(lab, 0.0)
            if isinstance(v, dict) and 'mean' in v:
                m = float(v.get('mean', 0.0))
                s = float(v.get('std', 0.0))
            else:
                m = float(v)
                s = 0.0
            means.append(max(0.0, min(max_scale, m)))
            stds.append(max(0.0, s))

        # 少于 3 维时改为条形图（这里固定为6维）
        if len(labels) < 3:
            with rc_context({'font.sans-serif': ['SimHei'], 'axes.unicode_minus': False}):
                fig, ax = plt.subplots(figsize=size, dpi=dpi)
                ax.bar(labels, means, color='#ff4d4f', alpha=0.85)
                ax.set_ylim(0, max_scale)
                ax.set_ylabel('分数(0-100)')
                ax.set_title('中医体质维度（条形图）', fontsize=14)
                if annotate:
                    for i, v in enumerate(means):
                        ax.text(i, v + max_scale * 0.02, f"{round(v,1)}", ha='center')
        else:
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
            angles_cycle = np.concatenate((angles, [angles[0]]))

            mean_cycle = np.concatenate((means, [means[0]]))
            upper = [min(max_scale, m + s) for m, s in zip(means, stds)]
            lower = [max(0.0, m - s) for m, s in zip(means, stds)]
            upper_cycle = np.concatenate((upper, [upper[0]]))
            lower_cycle = np.concatenate((lower, [lower[0]]))

            # 色板（柔和）
            green = '#66c2a5'
            yellow = '#ffd166'
            red = '#ef476f'
            band_color = '#ff9f1c'

            with rc_context({'font.sans-serif': ['SimHei'], 'axes.unicode_minus': False}):
                fig, ax = plt.subplots(figsize=size, subplot_kw=dict(polar=True), dpi=dpi)
                ax.set_ylim(0, max_scale)

                # 绘制分区背景（从外到内覆盖）
                ax.fill(angles_cycle, [max_scale] * len(angles_cycle), color=red, alpha=0.12)
                ax.fill(angles_cycle, [70] * len(angles_cycle), color=yellow, alpha=0.12)
                ax.fill(angles_cycle, [30] * len(angles_cycle), color=green, alpha=0.12)

                # 绘制置信带（均值 ± std）
                if any(s > 0 for s in stds):
                    ax.fill_between(angles, lower, upper, color=band_color, alpha=0.18)

                # 数据多边形与填充（均值）
                ax.plot(angles_cycle, mean_cycle, color='#ff4d4f', linewidth=2)
                ax.fill(angles_cycle, mean_cycle, color='#ff4d4f', alpha=0.25)

                # 标签：主标签 + 次级描述（换行）
                wrapped = [f"{d[0]}\n{d[1]}" for d in dims]
                ax.set_xticks(angles)
                ax.set_xticklabels(wrapped, fontsize=10)

                # 关键径向刻度（0/30/70/100）
                ax.set_yticks([0, 30, 70, 100])
                ax.set_yticklabels(['0', '30', '70', '100'], fontsize=9)
                ax.grid(ls='--', lw=0.8, color='gray', alpha=0.5)
                ax.set_title('中医体质多维分析图谱', y=1.08, fontsize=15)

                # 在顶点标注均值（并在必要时显示 std）
                if annotate:
                    for angle, m, s in zip(angles, means, stds):
                        txt = f"{round(m,1)}"
                        if s > 0:
                            txt += f" ±{round(s,1)}"
                        ax.text(angle, m + max_scale * 0.03, txt, ha='center', va='bottom', fontsize=9, color='#333')

                # 底部说明（分区含义与置信度）
                foot_parts = []
                foot_parts.append('中心绿区 (0-30)：平衡；中间黄区 (30-70)：波动；边缘红区 (70-100)：失衡')
                if overall_confidence is not None:
                    level = '低' if overall_confidence < 0.5 else ('中' if overall_confidence < 0.8 else '高')
                    foot_parts.append(f'本次分析置信度：{level} ({round(overall_confidence*100)}%)')
                if interpretation:
                    foot_parts.append(interpretation)
                foot = ' | '.join(foot_parts)
                if foot:
                    fig.text(0.5, 0.02, foot, ha='center', fontsize=10)

        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
        plt.close(fig)
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

                                            # 关键径向刻度（0/30/70/100）
                                            ax.set_yticks([0, 30, 70, 100])
                                            ax.set_yticklabels(['0', '30', '70', '100'], fontsize=9)
                                            ax.grid(ls='--', lw=0.8, color='gray', alpha=0.5)
                                            ax.set_title('中医体质多维分析图谱', y=1.08, fontsize=15)

                                            # 在顶点标注数值
                                            if annotate:
                                                for angle, val in zip(angles, values):
                                                    ax.text(angle, val + max_scale * 0.03, f"{round(val,1)}", ha='center', va='bottom', fontsize=9, color='#333')

                                            # 底部说明（分区含义与置信度）
                                            foot_parts = []
                                            foot_parts.append('中心绿区 (0-30)：平衡；中间黄区 (30-70)：波动；边缘红区 (70-100)：失衡')
                                            if overall_confidence is not None:
                                                level = '低' if overall_confidence < 0.5 else ('中' if overall_confidence < 0.8 else '高')
                                                foot_parts.append(f'本次分析置信度：{level} ({round(overall_confidence*100)}%)')
                                            if interpretation:
                                                foot_parts.append(interpretation)
                                            foot = ' | '.join(foot_parts)
                                            if foot:
                                                fig.text(0.5, 0.02, foot, ha='center', fontsize=10)

                                    buf = io.BytesIO()
                                    fig.tight_layout()
                                    fig.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
                                    plt.close(fig)
                                    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()