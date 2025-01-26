import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
import matplotlib

matplotlib.use('Agg')  # 使用非交互式后端

# 尝试加载自定义字体路径
try:
    font_paths = [
        os.path.join(os.path.dirname(__file__), "fonts/Symbola.ttf"),
        os.path.join(os.path.dirname(__file__), "fonts/NotoSerifSC[wght].ttf")
    ]
    font_loaded = False
    for font_path in font_paths:
        if os.path.exists(font_path):
            from matplotlib import font_manager as fm
            prop = fm.FontProperties(fname=font_path)
            rcParams['font.family'] = prop.get_name()
            print(f"Loaded font: {prop.get_name()} from {font_path}")
            font_loaded = True
            break
    if not font_loaded:
        print("Custom fonts not found, falling back to default.")
        rcParams['font.family'] = 'DejaVu Sans'  # 默认字体
except Exception as e:
    print(f"Error loading custom font: {e}. Using default font.")
    rcParams['font.family'] = 'DejaVu Sans'  # 默认字体

rcParams['axes.unicode_minus'] = False  # 确保负号正常显示

# 占星符号 Unicode 字符
planet_symbols = {
    'Sun': '\u2609', 'Moon': '\u263D', 'Mercury': '\u263F',
    'Venus': '\u2640', 'Mars': '\u2642', 'Jupiter': '\u2643',
    'Saturn': '\u2644', 'Uranus': '\u2645', 'Neptune': '\u2646', 'Pluto': '\u2647',
    'Asc': 'ASC', 'Desc': 'DESC', 'MC': 'MC', 'IC': 'IC'
}

def plot_natal_chart(planet_positions, output_path=None, show=True):
    """
    绘制命盘图。
    :param planet_positions: 字典，行星名称和其黄道经度
    :param output_path: 保存图像的路径，默认为 None。如果提供路径，则保存图像到指定位置。
    :param show: 是否显示图表，默认为 True
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
        ax.set_theta_zero_location('E')  # 将黄道的 0 度 (牡羊座) 设为东方
        ax.set_theta_direction(-1)       # 逆时针排列星座

        # 黄道十二星座
        zodiac_signs = ['\u2648', '\u2649', '\u264A', '\u264B', '\u264C', '\u264D',
                        '\u264E', '\u264F', '\u2650', '\u2651', '\u2652', '\u2653']
        zodiac_angles = np.linspace(0, 2 * np.pi, 13)[:-1]  # 每个星座的起始角度

        # 绘制星座分区
        for i, (angle, sign) in enumerate(zip(zodiac_angles, zodiac_signs)):
            color = 'yellow' if i % 2 == 0 else 'lightyellow'
            ax.fill_betweenx([0, 1], angle, angle + np.pi / 6, color=color, alpha=0.3)
            ax.text(angle + np.pi / 12, 1.1, sign, ha='center', va='center', fontsize=12, fontproperties=prop)

        # 绘制宫位分区
        house_angles = np.linspace(0, 2 * np.pi, 13)[:-1]
        for angle in house_angles:
            ax.plot([angle, angle], [0, 1], color='gray', linestyle='--', linewidth=0.5)

        # 绘制行星位置
        for planet, position in planet_positions.items():
            theta = np.deg2rad(position)
            ax.plot(theta, 0.8, 'o', markersize=10, label=f"{planet} ({position:.2f}\u00b0)")
            ax.text(theta, 0.9, planet_symbols.get(planet, planet), ha='center', va='center', fontsize=14, fontproperties=prop)

        # 绘制行星之间的相位连线
        planet_positions_rad = {k: np.deg2rad(v) for k, v in planet_positions.items()}
        for planet1, theta1 in planet_positions_rad.items():
            for planet2, theta2 in planet_positions_rad.items():
                angle_diff = np.abs(theta1 - theta2)
                if 0 < angle_diff < np.pi / 3:  # 例如：判断三分相
                    ax.plot([theta1, theta2], [0.8, 0.8], color='blue', linestyle='-', alpha=0.5)

        # 图表设置
        ax.set_yticks([])  # 隐藏径向刻度
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8, prop=prop)
        ax.set_title("命盘图", va='bottom', fontsize=16, pad=30, fontproperties=prop)

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

# 测试数据
test_positions = {
    'Sun': 295.5, 'Moon': 134.7, 'Mercury': 280.3, 'Venus': 342.6,
    'Mars': 116.4, 'Jupiter': 71.9, 'Saturn': 345.7,
    'Uranus': 53.3, 'Neptune': 357.5, 'Pluto': 301.5
}

plot_natal_chart(test_positions, output_path="natal_chart.png")
