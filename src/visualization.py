import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# 設置支持中文的字體
rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

def plot_natal_chart(planet_positions, show=True):
    # 繪製命盤圖邏輯
    pass

    """
    繪製命盤圖。
    :param planet_positions: 字典，行星名稱和其黃道經度
    """
    # 創建圖表
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('E')  # 將黃道的 0 度 (牡羊座) 設為東方
    ax.set_theta_direction(-1)       # 逆時針排列星座

    # 黃道十二星座
    zodiac_signs = [
        '牡羊座', '金牛座', '雙子座', '巨蟹座', '獅子座', '處女座',
        '天秤座', '天蠍座', '射手座', '摩羯座', '水瓶座', '雙魚座'
    ]
    zodiac_angles = np.linspace(0, 2 * np.pi, 13)[:-1]  # 每個星座的起始角度

    # 繪製星座分區
    for angle, sign in zip(zodiac_angles, zodiac_signs):
        ax.text(angle, 1.1, sign, ha='center', va='center', fontsize=10, color='blue')
        ax.plot([angle, angle], [0, 1], color='gray', linestyle='--', linewidth=0.5)

    # 繪製行星位置
    for planet, position in planet_positions.items():
        theta = np.deg2rad(position)  # 將度數轉為弧度
        ax.plot(theta, 0.8, 'o', label=f"{planet} ({position:.2f}°)", markersize=8)

    # 圖表設置
    ax.set_yticklabels([])  # 隱藏徑向刻度
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8)
    ax.set_title("命盤圖", va='bottom', fontsize=16)

    # 調整徑向刻度的位置
    ax.tick_params(axis='y', pad=100)  # 增加刻度與圓圈的距離（20 是距離的像素值）

    # 調整標題
    ax.set_title("命盤圖", va='bottom', fontsize=16, pad=30)

    # 調整整體布局
    fig.subplots_adjust(top=0.85)

    # 顯示圖表
    plt.show()




