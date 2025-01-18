import sys
import os
import matplotlib.pyplot as plt
from src.visualization import plot_natal_chart

def test_plot_natal_chart():
    # 模擬的行星位置
    positions = {
        'Sun': 88.5,
        'Moon': 342.2,
        'Mercury': 65.8,
        'Venus': 56.2,
        'Mars': 19.0,
        'Jupiter': 6.3,
        'Saturn': 325.1,
        'Uranus': 47.3,
        'Neptune': 355.4,
        'Pluto': 298.0
    }

    # 測試輸出文件夾
    output_folder = os.path.join(os.path.dirname(__file__), "../src/output")
    os.makedirs(output_folder, exist_ok=True)

    # 測試圖片保存路徑
    test_output_path = os.path.join(output_folder, "test_chart.png")

    # 繪製命盤圖並保存
    plot_natal_chart(positions, show=False)
    plt.savefig(test_output_path, dpi=300)
    plt.close()

    # 確認文件是否生成
    assert os.path.exists(test_output_path), "命盤圖生成失敗"

    # 清理測試文件
    os.remove(test_output_path)
