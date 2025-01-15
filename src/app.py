import uuid
import os
import matplotlib.pyplot as plt
from flask import Flask, request, send_file

from calculator import calculate_planet_positions
from visualization import plot_natal_chart

app = Flask(__name__)

@app.route("/")
def home():
    return "Server is running!"

@app.route('/favicon.ico')
def favicon():
    return '', 204  # 或返回實際圖標文件

@app.route('/generate-chart', methods=['POST'])
def generate_chart():
    if not request.is_json:
        return "Invalid request: Expected JSON", 400

    data = request.json
    year = data.get('year')
    month = data.get('month')
    day = data.get('day')
    hour = data.get('hour')
    minute = data.get('minute')

    if not all([year, month, day, hour, minute]):
        return "Invalid request: Missing required fields", 400

    # 計算行星位置
    positions = calculate_planet_positions(year, month, day, hour, minute)

    # 繪製並保存命盤圖
    output_path = f"natal_chart_{uuid.uuid4().hex}.png"
    plot_natal_chart(positions, show=False)
    plt.savefig(output_path, dpi=300)
    plt.close()

    # 返回結果
    return send_file(output_path, mimetype='image/png')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 默認為 5000
    app.run(host="0.0.0.0", port=port)