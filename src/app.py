import logging
import os
import time
import uuid

import matplotlib
from flask import Flask, request, jsonify, url_for, send_file

matplotlib.use('Agg')  # 非交互式后端

# 從 visualization 模組中匯入所需函式
from visualization import plot_natal_chart, get_planet_positions, get_julian_day_with_time

# 初始化日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/")
def home():
    return "Server is running!"

@app.route("/favicon.ico")
def favicon():
    icon_path = os.path.join(os.path.dirname(__file__), "static/favicon.ico")
    if os.path.exists(icon_path):
        return send_file(icon_path, mimetype="image/vnd.microsoft.icon")
    return '', 404

def calculate_aspects(planet_positions):
    """
    根據行星間角度，自動判斷主要相位（合相、六分相、四分相、拱相、對分）
    並傳回包含 (行星1, 行星2, color, diff) 的列表。
    """
    aspects_def = [
        (0, 8, 'purple'),   # 合相 orb=8
        (60, 6, 'green'),   # 六分相 orb=6
        (90, 6, 'blue'),    # 四分相 orb=6
        (120, 6, 'orange'), # 拱相 orb=6
        (180, 8, 'red')     # 對分相 orb=8
    ]
    aspect_lines = []
    planets = list(planet_positions.keys())
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            pos1 = planet_positions[planets[i]]['position']
            pos2 = planet_positions[planets[j]]['position']
            diff = abs(pos1 - pos2) % 360
            if diff > 180:
                diff = 360 - diff
            for aspect_angle, orb, color in aspects_def:
                if abs(diff - aspect_angle) <= orb:
                    aspect_lines.append((planets[i], planets[j], color, diff))
                    break
    return aspect_lines


@app.route("/generate-chart", methods=["POST"])
def generate_chart():
    # 確保請求內容為 JSON 格式
    if not request.is_json:
        logger.error("Invalid request: Expected JSON")
        return jsonify({"error": "Invalid request: Expected JSON"}), 400

    data = request.json
    year = data.get("year")
    month = data.get("month")
    day = data.get("day")
    hour = data.get("hour")
    minute = data.get("minute")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # 檢查必要欄位是否皆有提供
    if any(value is None for value in [year, month, day, hour, minute, latitude, longitude]):
        logger.error("Invalid request: Missing required fields")
        return jsonify({"error": "Invalid request: Missing required fields"}), 400

    # 建立輸出資料夾，並產生唯一檔名
    output_folder = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_folder, exist_ok=True)
    output_filename = f"natal_chart_{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_folder, output_filename)

    # 清理過期的舊檔案
    clean_output_folder(output_folder, max_age_seconds=3600)

    try:
        # 設定預設秒數與時區（此處固定為 UTC+8）
        second = 0
        timezone_offset = 8

        # 計算 Julian Day，使用客戶端輸入的出生年月日時分，以及從請求中取得的經緯度（在此僅用於 house 計算）
        julian_day = get_julian_day_with_time(year, month, day, hour, minute, second, timezone_offset)

        # 計算行星位置，結果格式為 { 'Sun': {'position': ..., 'retrograde': ..., 'speed': ...}, ... }
        positions = get_planet_positions(julian_day)
        logger.info(f"Calculated positions: {positions}")

        # 計算相位線
        aspect_lines = calculate_aspects(positions)
    except Exception as e:
        logger.error(f"Error calculating positions or aspects: {e}")
        return jsonify({"error": "Error occurred during calculation."}), 500

    # 更新檔案名稱（以確保唯一性），並產生完整路徑
    output_filename = f"natal_chart_{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_folder, output_filename)
    try:
        # 呼叫繪圖函式，傳入行星位置、julian_day 以及客戶端提供的經緯度
        plot_natal_chart(positions, julian_day, latitude, longitude,
                         aspect_lines=aspect_lines, output_path=output_path, show=False)
        logger.info(f"Chart saved successfully to: {output_path}")
    except Exception as e:
        logger.error(f"Error saving chart: {e}")
        return jsonify({"error": "Error occurred while generating the chart."}), 500

    # 回傳圖片 URL 以及使用者輸入的經緯度資訊
    chart_url = url_for('serve_output_file', filename=output_filename, _external=True)
    return jsonify({
        "message": "Chart generated successfully",
        "chart_url": chart_url,
        "latitude": latitude,
        "longitude": longitude
    }), 200

@app.route("/output/<filename>")
def serve_output_file(filename):
    output_folder = os.path.join(os.path.dirname(__file__), "output")
    file_path = os.path.abspath(os.path.join(output_folder, filename))

    # 驗證路徑安全性
    if not file_path.startswith(os.path.abspath(output_folder)):
        logger.error(f"Attempted access to unsafe path: {file_path}")
        return jsonify({"error": "Access denied"}), 403

    if os.path.exists(file_path):
        logger.info(f"File found: {file_path}")
        return send_file(file_path, mimetype="image/png")

    logger.error(f"File not found: {filename}")
    return jsonify({"error": "File not found"}), 404

@app.route("/ai-plugin.json")
def serve_ai_plugin():
    return serve_static_file("ai-plugin.json", "application/json")

@app.route("/openapi.json")
def serve_openapi():
    return serve_static_file("openapi.json", "application/json")

@app.route("/privacy-policy")
def privacy_policy():
    return serve_static_file("privacy-policy.html", "text/html")

def serve_static_file(filename, mimetype):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, str(filename))

    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, mimetype=str(mimetype))

    logger.error(f"File not found: {file_path}")
    return jsonify({"error": f"{filename} not found"}), 404

def clean_output_folder(folder_path, max_age_seconds=3600):
    folder_path = os.path.abspath(folder_path)
    now = time.time()
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and now - os.path.getmtime(file_path) > max_age_seconds:
            os.remove(file_path)
            logger.info(f"Removed old file: {file_path}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Current working directory: {os.getcwd()}")
    app.run(host="0.0.0.0", port=port)
