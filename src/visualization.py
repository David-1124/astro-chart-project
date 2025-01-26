import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from matplotlib.patches import Circle
from matplotlib import font_manager as fm
import matplotlib

matplotlib.use('Agg')  # 使用非交互式后端

# 尝试加载 Symbola 字体
try:
    font_path = os.path.join(os.path.dirname(__file__), "fonts/Symbola.ttf")
    if os.path.exists(font_path):
        prop = fm.FontProperties(fname=font_path)
        rcParams['font.family'] = prop.get_name()
        print(f"Loaded font: {prop.get_name()}")
    else:
        print("Symbola font not found, falling back to default.")
        prop = fm.FontProperties(family='DejaVu Sans')  # 默认字体
except Exception as e:
    print(f"Error loading font: {e}. Using default font.")
    prop = fm.FontProperties(family='DejaVu Sans')  # 默认字体

rcParams['axes.unicode_minus'] = False  # 确保负号正常显示

# 黃道十二星座名称
zodiac_signs = [
    '\u2648', '\u2649', '\u264A', '\u264B', '\u264C', '\u264D',
    '\u264E', '\u264F', '\u2650', '\u2651', '\u2652', '\u2653'
]
zodiac_names = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

def get_zodiac_sign(degree):
    """计算度数所属的星座"""
    index = int(degree // 30) % 12
    return f"{zodiac_names[index]} {degree % 30:.2f}°"

def get_house(degree):
    """计算度数所属的宫位 (假设每个宫位30度分布)"""
    return (int(degree // 30) % 12) + 1

def plot_natal_chart(planet_positions, aspect_lines=None, output_path=None, show=True):
    """
    绘制带有多层同心圆的命盘图并添加表格。
    """
    try:
        fig, ax = plt.subplots(figsize=(14, 10), subplot_kw={'projection': 'polar'})
        ax.set_theta_zero_location('E')  # 将黄道的 0 度 (牡羊座) 设为东
        ax.set_theta_direction(-1)       # 逆时针排列星座

        # 绘制同心圆
        for r in [0.6, 0.7, 0.8, 1.0]:  # 半径列表
            ax.add_patch(Circle((0, 0), r, transform=ax.transData._b, color='black', fill=False, linewidth=0.5))

        # 星座符号及其角度
        zodiac_angles = np.linspace(0, 2 * np.pi, 13)[:-1]  # 每个星座的起始角度
        angle_offset = (2 * np.pi / 12) / 2  # 偏移角度，使符号位于分割线中间

        # 定义星座符号的颜色
        zodiac_colors = [
            "red", "orange", "black", "green", "blue", "indigo",
            "violet", "cyan", "magenta", "gold", "pink", "lime"
        ]

        # 绘制星座符号（放置于空格内）
        for angle, sign, color in zip(zodiac_angles, zodiac_signs, zodiac_colors):
            adjusted_angle = angle + angle_offset  # 调整角度使其位于空格内
            ax.text(adjusted_angle, 0.92, sign, ha='center', va='center', fontsize=20,
                    fontproperties=prop, color=color)  # 符号位置
            ax.plot([angle, angle], [0.8, 1.0], color='black', linestyle='--', linewidth=0.5)  # 星座分割线

        # 绘制黄道十二宫（位于星座与行星之间）
        houses = [f" {i}" for i in range(1, 13)]
        for angle, house in zip(zodiac_angles, houses):
            adjusted_angle = angle + angle_offset
            ax.text(adjusted_angle, 0.75, house, ha='center', va='center', fontsize=10, fontproperties=prop)

        # 绘制行星位置
        planet_markers = {"\u2609": 'o', "\u263D": 's', "\u2642": '^', "\u2640": 'D', "\u263F": 'p',
                          "\u2643": '*', "\u2644": 'H', "\u2645": 'd', "\u2646": 'v', "\u2647": 'h'}
        zodiac_degrees = {}
        houses = {}
        for planet, position in planet_positions.items():
            theta = np.deg2rad(position)
            ax.plot(theta, 0.6, planet_markers.get(planet, 'o'), markersize=10)
            ax.text(theta, 0.65, planet, ha='center', va='center', fontsize=16, fontproperties=prop)
            zodiac_degrees[planet] = get_zodiac_sign(position)
            houses[planet] = get_house(position)

        # 绘制宫位分区（缩小半径）
        house_angles = np.linspace(0, 2 * np.pi, 13)[:-1]
        for angle in house_angles:
            ax.plot([angle, angle], [0, 0.8], color='gray', linestyle='--', linewidth=0.5)

        # 绘制相位线（最内圈）
        if aspect_lines:
            for planet1, planet2, color in aspect_lines:
                pos1 = np.deg2rad(planet_positions.get(planet1, 0))
                pos2 = np.deg2rad(planet_positions.get(planet2, 0))
                ax.plot([pos1, pos2], [0.6, 0.6], color=color, linestyle='-', linewidth=1, alpha=0.7)

        # 添加表格
        table_data = []
        for planet, zodiac_info in zodiac_degrees.items():
            house = houses.get(planet, '-')
            table_data.append([planet, zodiac_info, house])

        column_labels = ["Planet", "Zodiac (Degrees)", "House"]
        table = plt.table(
            cellText=table_data,
            colLabels=column_labels,
            loc='center',
            cellLoc='center',
            bbox=[0.8, 0.9, 0.3, 0.3]  # 表格放置在星盘的右上角
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)  # 表格字体大小
        table.auto_set_column_width(col=list(range(len(column_labels))))  # 自动调整列宽

        # 图表设置
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_title("Natal Chart", va='bottom', fontsize=16, pad=30, fontproperties=prop)

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
planet_positions = {
    "\u2609": 10,  # 太阳
    "\u263D": 120,  # 月亮
    "\u2642": 180,  # 火星
    "\u2640": 240,  # 金星
    "\u263F": 300,  # 水星
    "\u2643": 45,   # 木星
    "\u2644": 135,  # 土星
    "\u2645": 225,  # 天王星
    "\u2646": 315,  # 海王星
    "\u2647": 90    # 冥王星
}

aspect_lines = [
    ("\u2609", "\u263D", "red"),
    ("\u2642", "\u2640", "blue"),
    ("\u263F", "\u2643", "green")
]

plot_natal_chart(planet_positions, aspect_lines, output_path="natal_chart_with_table.png", show=False)
