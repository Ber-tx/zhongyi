import matplotlib

matplotlib.use('Agg')  # 防止在无显示器的服务器环境报错
import matplotlib.pyplot as plt
import numpy as np
import io, base64
from matplotlib import rc_context
import os  # 新增：用于处理路径
from matplotlib import font_manager  # 新增：用于加载本地字体


class Visualizer:
    @staticmethod
    def generate_radar(scores_dict,
                       interpretation: str = None,
                       overall_confidence: float = None,
                       size=(7, 7),
                       dpi=200,
                       max_scale=100,
                       annotate=True):
        """生成带有刻度、分区背景和简短文字解读的雷达图。

        支持两种 `scores_dict` 格式：
        - {dim: number}
        - {dim: {'mean': number, 'std': number}}

        返回 data URL (png)
        """
        # --- 1. 加载本地字体文件 ---

        font_path = os.path.join(os.path.dirname(__file__), 'SimHei.otf')
        if not os.path.exists(font_path):
            # 如果是交互式环境或找不到 __file__，尝试当前路径
            font_path = 'SimHei.otf'

        # 创建字体属性对象
        prop = font_manager.FontProperties(fname=font_path)
        if not isinstance(scores_dict, dict) or len(scores_dict) == 0:
            raise ValueError('scores_dict must be a non-empty dict')

        # 动态维度：优先使用传入键名，避免键名升级后出现全 0 渲染
        detail_map = {
            "舌色偏红指数": "舌色红绛/热象倾向",
            "舌色偏淡指数": "舌色淡白/虚寒倾向",
            "苔色黄腻指数": "黄腻苔/湿热痰浊",
            "瘀血征象指数": "紫暗斑点/瘀阻倾向",
            "津液亏虚指数": "干燥少津/阴液不足",

        }
        labels = list(scores_dict.keys())
        dims = [(lab, detail_map.get(lab, "结构化指标")) for lab in labels]

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

        # --- 强冲击力配色方案 ---
        color_main = '#FF0000'  # 纯正大红（数据连线）
        color_fill = '#FF000033'  # 红色填充

        # 极高饱和度的分区背景
        bg_green = '#00FF00'  # 荧光绿
        bg_yellow = '#FFFF00'  # 纯黄
        bg_red = '#FF3300'  # 亮红

        # 少于 3 维时改为条形图（这里固定为6维）
        if len(labels) < 3:
            fig, ax = plt.subplots(figsize=size, dpi=dpi)
            ax.bar(labels, means, color=color_main, alpha=0.85)
            ax.set_ylim(0, max_scale)
            ax.set_ylabel('分数(0-100)', fontproperties=prop, fontsize=16)  # 增大
            ax.set_title('中医体质维度（条形图）', fontproperties=prop, fontsize=20)  # 增大
            # 设置横轴中文
            ax.set_xticklabels(labels, fontproperties=prop, fontsize=14)  # 增大
            if annotate:
                for i, v in enumerate(means):
                    ax.text(i, v + max_scale * 0.02, f"{round(v, 1)}", ha='center', fontsize=14)  # 增大
        else:
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
            angles_cycle = np.concatenate((angles, [angles[0]]))
            mean_cycle = np.concatenate((means, [means[0]]))
            upper = [min(max_scale, m + s) for m, s in zip(means, stds)]
            lower = [max(0.0, m - s) for m, s in zip(means, stds)]

            green, yellow, red = bg_green, bg_yellow, bg_red

            fig, ax = plt.subplots(figsize=size, subplot_kw=dict(polar=True), dpi=dpi)
            ax.set_ylim(0, max_scale)

            # 绘制极鲜明的分区背景
            ax.fill(angles_cycle, [max_scale] * len(angles_cycle), color=red, alpha=0.15)
            ax.fill(angles_cycle, [70] * len(angles_cycle), color=yellow, alpha=0.20)
            ax.fill(angles_cycle, [30] * len(angles_cycle), color=green, alpha=0.25)

            # 绘制置信带
            if any(s > 0 for s in stds):
                ax.fill_between(angles, lower, upper, color='#FFA500', alpha=0.3)

            # 绘制红色主体连线
            ax.plot(angles_cycle, mean_cycle, color=color_main, linewidth=1.5, marker='o',
                    markersize=4, markerfacecolor='white', markeredgewidth=2)  # 增大点尺寸
            ax.fill(angles_cycle, mean_cycle, color=color_fill)

            wrapped = [f"{d[0]}\n{d[1]}" for d in dims]
            ax.set_xticks(angles)
            # 增大：雷达图外圈维度标签字号
            ax.set_xticklabels(wrapped, fontproperties=prop, fontsize=13, fontweight='bold', color='#111')

            # 增大：径向刻度字号（0, 30, 70, 100）
            ax.set_yticks([0, 30, 70, 100])
            ax.set_yticklabels(['0', '30', '70', '100'], fontsize=12, fontweight='bold')
            ax.grid(ls='-', lw=1.2, color='#666666', alpha=0.4)

            # 增大：总标题字号
            ax.set_title('舌像结构化多维分析图谱', y=1.12, fontproperties=prop, fontsize=24, fontweight='bold')

            if annotate:
                for angle, m, s in zip(angles, means, stds):
                    txt = f"{round(m, 1)}"
                    if s > 0:
                        txt += f" ±{round(s, 1)}"
                    # 增大：顶点数值标注字号
                    ax.text(angle, m + max_scale * 0.06, txt, ha='center', va='bottom',
                            fontsize=11, color=color_main, fontweight='bold')

            foot_parts = []
            foot_parts.append('中心绿区 (0-30)：平衡；中间黄区 (30-70)：波动；边缘红区 (70-100)：失衡')
            if overall_confidence is not None:
                level = '低' if overall_confidence < 0.5 else ('中' if overall_confidence < 0.8 else '高')
                foot_parts.append(f'本次分析置信度：{level} ({round(overall_confidence * 100)}%)')
            if interpretation:
                foot_parts.append(interpretation)

            foot = ' | '.join(foot_parts)
            if foot:
                # 增大：底部脚注文字字号
                fig.text(0.5, 0.01, foot, ha='center', fontproperties=prop, fontsize=20, color='#333')

        buf = io.BytesIO()
        # 由于字体增大，调整布局防止文字溢出
        fig.tight_layout(rect=[0, 0.05, 1, 0.95])
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
        plt.close(fig)
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# 测试代码保持不变
# if __name__ == "__main__":
#     test_scores = {
#         "气血状态": 85.0,
#         "体液滋润度": 30.5,
#         "湿浊程度": 75.0,
#         "脾胃状态": 60.2,
#         "血脉通畅度": 95.0,
#         "外邪影响": 20.0
#     }
#     try:
#         result_base64 = Visualizer.generate_radar(
#             scores_dict=test_scores,
#             interpretation="红色高亮大字体版本测试。",
#             overall_confidence=0.88
#         )
#         if result_base64.startswith("data:image/png;base64,"):
#             header, encoded = result_base64.split(",", 1)
#             with open("debug_radar_large_font.png", "wb") as f:
#                 f.write(base64.b64decode(encoded))
#             print("✅ 预览图片已保存至: debug_radar_large_font.png")
#     except Exception as e:
#         print(f"❌ 运行报错: {str(e)}")