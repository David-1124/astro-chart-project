import logging
import os
import time
import uuid

import matplotlib
from flask import Flask, request, jsonify, url_for, send_file

matplotlib.use('Agg')  # 非交互式后端
from calculator import calculate_planet_positions
from visualization import plot_natal_chart, get_julian_day_with_time  # 新增导入 get_julian_day_with_time

# 初始化日志
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

# 相位线计算逻辑
def calculate_aspects(positions):
    """计算相位线"""
    aspects = []
    aspect_rules = {
        "conjunction": 0,
        "opposition": 180,
        "trine": 120,
        "square": 90
    }
    tolerance = 5  # 容差范围（度数）
    for planet1, pos1 in positions.items():
        for planet2, pos2 in positions.items():
            if planet1 != planet2:
                angle = abs(pos1 - pos2) % 360
                for aspect, target_angle in aspect_rules.items():
                    if abs(angle - target_angle) <= tolerance:
                        color = {"conjunction": "red", "opposition": "blue",
                                 "trine": "green", "square": "orange"}.get(aspect, "black")
                        aspects.append((planet1, planet2, color))
    return aspects

@app.route("/generate-chart", methods=["POST"])
def generate_chart():
    if not request.is_json:
        logger.error("Invalid request: Expected JSON")
        return jsonify({"error": "Invalid request: Expected JSON"}), 400

    data = request.json
    year = data.get("year")
    month = data.get("month")
    day = data.get("day")
    hour = data.get("hour")
    minute = data.get("minute")

    if any(value is None for value in [year, month, day, hour, minute]):
        logger.error("Invalid request: Missing required fields")
        return jsonify({"error": "Invalid request: Missing required fields"}), 400

    output_folder = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_folder, exist_ok=True)

    # 清理旧文件
    clean_output_folder(output_folder, max_age_seconds=3600)

    try:
        # 使用 calculator.py 中的 calculate_planet_positions 计算行星位置
        positions = calculate_planet_positions(year, month, day, hour, minute)
        logger.info(f"Calculated positions: {positions}")

        # 计算相位线
        aspect_lines = calculate_aspects(positions)
    except Exception as e:
        logger.error(f"Error calculating positions or aspects: {e}")
        return jsonify({"error": "Error occurred during calculation."}), 500

    # 这里补充默认值：秒=0，时区=8（台北），以及默认经纬度
    second = 0
    timezone_offset = 8
    latitude, longitude = 25.033, 121.565
    # 利用 visualization.get_julian_day_with_time 计算 julian_day
    julian_day = get_julian_day_with_time(year, month, day, hour, minute, second, timezone_offset)

    output_filename = f"natal_chart_{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_folder, output_filename)
    try:
        # 修改调用：传入 positions, julian_day, latitude, longitude 以及 aspect_lines、output_path、show=False
        plot_natal_chart(positions, julian_day, latitude, longitude,
                         aspect_lines=aspect_lines, output_path=output_path, show=False)
        logger.info(f"Chart saved successfully to: {output_path}")
    except Exception as e:
        logger.error(f"Error saving chart: {e}")
        return jsonify({"error": "Error occurred while generating the chart."}), 500

    # 返回图片 URL
    chart_url = url_for('serve_output_file', filename=output_filename, _external=True)
    return jsonify({"message": "Chart generated successfully", "chart_url": chart_url}), 200

@app.route("/output/<filename>")
def serve_output_file(filename):
    output_folder = os.path.join(os.path.dirname(__file__), "output")
    file_path = os.path.abspath(os.path.join(output_folder, filename))

    # 验证路径安全性
    if not file_path.startswith(os.path.abspath(output_folder)):
        logger.error(f"Attempted access to unsafe path: {file_path}")
        return jsonify({"error": "Access denied"}), 403

    if os.path.exists(file_path):
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

# 通用静态文件处理器
def serve_static_file(filename, mimetype):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype=mimetype)
    logger.error(f"{filename} file not found")
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
