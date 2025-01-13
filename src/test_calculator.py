from src.calculator import calculate_planet_positions
from src.utils import format_positions

def test_chart():
    # 測試輸入數據
    year, month, day, hour, minute = 1990, 5, 21, 14, 30

    # 計算命盤
    positions = calculate_planet_positions(year, month, day, hour, minute)
    print(format_positions(positions))

if __name__ == "__main__":
    test_chart()
