import sys
import os
import json
from src.app import app

# 將專案的 src 資料夾添加到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from src.app import app  # 或其他需要的模組


def test_generate_chart_route():
    app.testing = True  # 啟用測試模式
    client = app.test_client()

    # 模擬請求的 JSON 數據
    payload = {
        "year": 2025,
        "month": 1,
        "day": 15,
        "hour": 12,
        "minute": 0
    }

    # 發送 POST 請求
    response = client.post("/generate-chart", json=payload)

    # 確認 HTTP 狀態碼為 200
    assert response.status_code == 200, f"預期狀態碼 200，實際為 {response.status_code}"

    # 確認返回的文件是否為 PNG 圖片
    assert response.mimetype == "image/png", "返回的文件類型不是 PNG 圖片"

    # 確認生成的圖像是否存在於 output 文件夾中
    output_folder = os.path.join(os.path.dirname(__file__), "../src/output")
    generated_files = os.listdir(output_folder)
    assert len(generated_files) > 0, "未生成任何圖片"

    # 清理測試生成的文件
    for file in generated_files:
        os.remove(os.path.join(output_folder, file))
