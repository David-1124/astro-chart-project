import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
import matplotlib

matplotlib.use('Agg')  # 使用非交互式后端

# 设置字体为 Matplotlib 内置字体 DejaVu Sans
rcParams['font.family'] = 'DejaVu Sans'
rcParams['axes.unicode_minus'] = False  # 确保负号正常显示

def plot_natal_chart(planet_positions, output_path=None, show=True):
    """
    绘制命盘图。
    :param planet_positions: 字典，行星名称和其黄道经度
    :param output_path: 保存图像的路径，默认为 None。如果提供路径，则保存图像到指定位置。
    :param show: 是否显示图表，默认为 True
    """
    try:
        # 创建极坐标图表
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
        ax.set_theta_zero_location('E')  # 将黄道的 0 度 (牡羊座) 设为东方
        ax.set_theta_direction(-1)       # 逆时针排列星座

        # 黄道十二星座
        zodiac_signs = [
            '牡羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座',
            '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'
        ]
        zodiac_angles = np.linspace(0, 2 * np.pi, 13)[:-1]  # 每个星座的起始角度

        # 绘制星座分区
        for angle, sign in zip(zodiac_angles, zodiac_signs):
            ax.text(angle, 1.1, sign, ha='center', va='center', fontsize=10,
                    color='blue')  # 显示星座名称
            ax.plot([angle, angle], [0, 1], color='gray', linestyle='--', linewidth=0.5)  # 绘制分隔线

        # 绘制行星位置
        for planet, position in planet_positions.items():
            theta = np.deg2rad(position)  # 将度数转为弧度
            ax.plot(theta, 0.8, 'o', label=f"{planet} ({position:.2f}°)", markersize=8)

        # 设置图表标题和图例
        ax.set_yticklabels([])  # 隐藏径向刻度
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8)
        ax.set_title("命盘图", va='bottom', fontsize=16, pad=30)

        # 调整径向刻度的位置
        ax.tick_params(axis='y', pad=20)  # 增加刻度与圆圈的距离

        # 调整整体布局
        fig.subplots_adjust(top=0.85)

        # 保存或显示图表
        if output_path:
            print(f"Saving chart to: {output_path}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')  # 保存为文件
            print(f"Chart saved successfully to: {output_path}")
        if show:
            plt.show()
        else:
            plt.close(fig)  # 关闭图表以释放资源
    except Exception as e:
        print(f"An error occurred while plotting the natal chart: {e}")
