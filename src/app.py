import os
import uuid
import time
from flask import Flask, request, send_file, send_from_directory
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
from calculator import calculate_planet_positions
from visualization import plot_natal_chart
import logging

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

@app.route("/generate-chart", methods=["POST"])
def generate_chart():
    if not request.is_json:
        logger.error("Invalid request: Expected JSON")
        return "Invalid request: Expected JSON", 400

    data = request.json
    year = data.get("year")
    month = data.get("month")
    day = data.get("day")
    hour = data.get("hour")
    minute = data.get("minute")

    if any(value is None for value in [year, month, day, hour, minute]):
        logger.error("Invalid request: Missing required fields")
        return "Invalid request: Missing required fields", 400

    output_folder = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_folder, exist_ok=True)

    # 清理旧文件
    clean_output_folder(output_folder, max_age_seconds=3600)

    try:
        positions = calculate_planet_positions(year, month, day, hour, minute)
        logger.info(f"Calculated positions: {positions}")
    except Exception as e:
        logger.error(f"Error calculating positions: {e}")
        return "Error occurred during calculation.", 500

    output_path = os.path.join(output_folder, f"natal_chart_{uuid.uuid4().hex}.png")
    try:
        plot_natal_chart(positions, output_path=output_path, show=False)
        logger.info(f"Chart saved successfully to: {output_path}")
    except Exception as e:
        logger.error(f"Error saving chart: {e}")
        return "Error occurred while generating the chart.", 500

    return send_file(output_path, mimetype="image/png")

@app.route("/ai-plugin.json")
def serve_ai_plugin():
    plugin_path = os.path.join(os.path.dirname(__file__), "ai-plugin.json")
    if os.path.exists(plugin_path):
        return send_file(plugin_path, mimetype="application/json")
    logger.error("ai-plugin.json file not found")
    return "ai-plugin.json file not found", 404

@app.route("/openapi.json")
def serve_openapi():
    openapi_path = os.path.join(os.path.dirname(__file__), "openapi.json")
    if os.path.exists(openapi_path):
        return send_file(openapi_path, mimetype="application/json")
    logger.error("openapi.json file not found")
    return "openapi.json file not found", 404


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
