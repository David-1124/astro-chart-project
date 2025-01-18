import os
import uuid
from flask import Flask, request, send_file
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from calculator import calculate_planet_positions
from visualization import plot_natal_chart

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
        return "Invalid request: Expected JSON", 400

    data = request.json
    year = data.get("year")
    month = data.get("month")
    day = data.get("day")
    hour = data.get("hour")
    minute = data.get("minute")

    if any(value is None for value in [year, month, day, hour, minute]):
        return "Invalid request: Missing required fields", 400

    try:
        positions = calculate_planet_positions(year, month, day, hour, minute)
        print(f"Calculated positions: {positions}")
    except Exception as e:
        return f"Error calculating planet positions: {e}", 500

    output_folder = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"natal_chart_{uuid.uuid4().hex}.png")
    print(f"Saving chart to: {output_path}")

    try:
        plot_natal_chart(positions, output_path=output_path, show=False)
        print(f"Chart saved successfully to {output_path}")
    except Exception as e:
        print(f"Error saving chart: {e}")
        return f"Error generating chart: {e}", 500

    return send_file(output_path, mimetype="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Current working directory: {os.getcwd()}")
    app.run(host="0.0.0.0", port=port)
