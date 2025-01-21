import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
import matplotlib

matplotlib.use('Agg')  # 使用非交互式后端

# 尝试加载自定义字体路径，如果失败则回退到默认字体
try:
    font_path = os.path.join(os.path.dirname(__file__), "fonts/msjh.ttc")
    if os.path.exists(font_path):
        from matplotlib import font_manager as fm
        prop = fm.FontProperties(fname=font_path)
        rcParams['font.family'] = prop.get_name()
    else:
        raise FileNotFoundError("Custom font not found, falling back to default.")
except Exception as e:
    print(f"Error loading custom font: {e}. Using default font.")
    rcParams['font.family'] = 'DejaVu Sans'  # 默认字体
rcParams['axes.unicode_minus'] = False  # 确保负号正常显示

def plot_natal_chart(planet_positions, output_path=None, show=True):
    """
    绘制命盘图。
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
        ax.set_theta_zero_location('E')
        ax.set_theta_direction(-1)

        zodiac_signs = [
            '牡羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座',
            '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'
        ]
        zodiac_angles = np.linspace(0, 2 * np.pi, 13)[:-1]

        for angle, sign in zip(zodiac_angles, zodiac_signs):
            ax.text(angle, 1.1, sign, ha='center', va='center', fontsize=10, color='blue')
            ax.plot([angle, angle], [0, 1], color='gray', linestyle='--', linewidth=0.5)

        for planet, position in planet_positions.items():
            theta = np.deg2rad(position)
            ax.plot(theta, 0.8, 'o', label=f"{planet} ({position:.2f}°)", markersize=8)

        ax.set_yticklabels([])
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8)
        ax.set_title("命盘图", va='bottom', fontsize=16, pad=30)
        fig.subplots_adjust(top=0.85)

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
