import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
import matplotlib

matplotlib.use('Agg')  # 使用非交互式后端

# 尝试加载自定义字体路径
try:
    font_path = os.path.join(os.path.dirname(__file__), "fonts/NotoSerifSC[wght].ttf")
    if os.path.exists(font_path):
        from matplotlib import font_manager as fm
        prop = fm.FontProperties(fname=font_path)
        rcParams['font.family'] = prop.get_name()
        print(f"Loaded font: {prop.get_name()}")
    else:
        print("Custom font not found, falling back to default.")
        rcParams['font.family'] = 'DejaVu Sans'  # 默认字体
except Exception as e:
    print(f"Error loading custom font: {e}. Using default font.")
    rcParams['font.family'] = 'DejaVu Sans'  # 默认字体

rcParams['axes.unicode_minus'] = False  # 确保负号正常显示

def plot_natal_chart(planet_positions, aspect_lines=None, output_path=None, show=True):
    """
    绘制命盘图。
    :param planet_positions: 字典，行星名称和其黄道经度
    :param aspect_lines: 列表，包含相位信息，如 [(行星1, 行星2, 相位颜色)]
    :param output_path: 保存图像的路径，默认为 None。如果提供路径，则保存图像到指定位置。
    :param show: 是否显示图表，默认为 True
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
        ax.set_theta_zero_location('E')  # 将黄道的 0 度 (牡羊座) 设为东方
        ax.set_theta_direction(-1)       # 逆时针排列星座

        # 黄道十二星座符号
        zodiac_signs = [
            '\u2648', '\u2649', '\u264A', '\u264B', '\u264C', '\u264D',  # Aries 到 Virgo
            '\u264E', '\u264F', '\u2650', '\u2651', '\u2652', '\u2653'   # Libra 到 Pisces
        ]
        zodiac_angles = np.linspace(0, 2 * np.pi, 13)[:-1]  # 每个星座的起始角度

        # 绘制星座分区
        for angle, sign in zip(zodiac_angles, zodiac_signs):
            ax.text(angle, 1.1, sign, ha='center', va='center', fontsize=12, color='blue')
            ax.plot([angle, angle], [0, 1], color='gray', linestyle='--', linewidth=0.5)

        # 绘制行星位置
        planet_markers = {"☉": 'o', "☽": 's', "♂": '^', "♀": 'D', "☿": 'p', "♃": '*', "♄": 'H', "♅": 'd', "♆": 'v', "♇": 'h'}
        for planet, position in planet_positions.items():
            theta = np.deg2rad(position)
            ax.plot(theta, 0.8, planet_markers.get(planet, 'o'), label=f"{planet} ({position:.2f}°)", markersize=8)

        # 绘制相位线
        if aspect_lines:
            for planet1, planet2, color in aspect_lines:
                pos1 = np.deg2rad(planet_positions.get(planet1, 0))
                pos2 = np.deg2rad(planet_positions.get(planet2, 0))
                ax.plot([pos1, pos2], [0.8, 0.8], color=color, linestyle='-', linewidth=1)

        # 图表设置
        ax.set_yticklabels([])
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8)
        ax.set_title("命盘图", va='bottom', fontsize=16, pad=30)
        fig.subplots_adjust(top=0.85)

        # 保存或显示图表
        if output_path:
            print(f"Saving chart to: {output_path}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved successfully to: {output_path}")
        if show:
            plt.show()
        else:
            plt.close(fig)
    except Exception as e:
        print(f"An error occurred while plotting the natal chart: {e}")

# 示例使用
planet_positions = {
    "☉": 10,
    "☽": 120,
    "♂": 180,
    "♀": 240,
    "☿": 300,
    "♃": 45,
    "♄": 135,
    "♅": 225,
    "♆": 315,
    "♇": 90
}

aspect_lines = [
    ("☉", "☽", "red"),
    ("♂", "♀", "blue"),
    ("☿", "♃", "green")
]

plot_natal_chart(planet_positions, aspect_lines, output_path="natal_chart.png", show=False)
