from calculator import calculate_planet_positions
from visualization import plot_natal_chart
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # 獲取使用者輸入
    year = int(input("請輸入出生年份："))
    month = int(input("請輸入出生月份："))
    day = int(input("請輸入出生日："))
    hour = int(input("請輸入出生小時（24小時制）："))
    minute = int(input("請輸入出生分鐘："))

    # 計算行星位置
    positions = calculate_planet_positions(year, month, day, hour, minute)

    # 輸出行星位置
    print("行星位置：")
    for planet, pos in positions.items():
        print(f"{planet}: {pos:.2f}°")

    # 繪製命盤圖
    print("正在生成命盤圖...")
    plot_natal_chart(positions)

    # 匯出圖表
    output_path = f"natal_chart_{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}.png"
    plt.savefig(output_path, dpi=300)
    print(f"命盤圖已保存為 {output_path}")