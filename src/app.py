import matplotlib.pyplot as plt
from src.calculator import calculate_planet_positions
from flask import Flask, request, send_file
from visualization import plot_natal_chart
import sys
import os

# 將專案根目錄添加到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

@app.route('/generate-chart', methods=['POST'])
def generate_chart():
    # 獲取用戶輸入
    data = request.json
    year = data.get('year')
    month = data.get('month')
    day = data.get('day')
    hour = data.get('hour')
    minute = data.get('minute')

    # 計算行星位置
    positions = calculate_planet_positions(year, month, day, hour, minute)

    # 繪製並保存命盤圖
    output_path = f"natal_chart_{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}.png"
    plot_natal_chart(positions, show=False)  # 不顯示圖表
    plt.savefig(output_path, dpi=300)
    plt.close()

    # 返回結果
    return send_file(output_path, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

@app.route('/favicon.ico')
def favicon():
    return '', 204  # 返回空內容，HTTP 狀態碼 204 表示無內容

@app.route('/favicon.ico')
def favicon():
    return send_file('path/to/favicon.ico', mimetype='image/vnd.microsoft.icon')