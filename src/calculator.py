import swisseph as swe
import os

# 設定 Swiss Ephemeris 的數據路徑（相對路徑）
DATA_PATH = os.path.join(os.path.dirname(__file__), "C:/Users/User/PycharmProjects/PythonProject/data")

def calculate_planet_positions(year, month, day, hour, minute):
    """
    計算行星在命盤中的位置。
    :param year: 出生年份
    :param month: 出生月份
    :param day: 出生日
    :param hour: 出生小時
    :param minute: 出生分鐘
    :return: 行星位置字典
    """
    # 設定天文數據路徑
    swe.set_ephe_path(DATA_PATH)

    # 計算 Julian Day (JD)
    utc_time = hour + minute / 60.0
    jd = swe.julday(year, month, day, utc_time)

    # 定義需要計算的行星列表
    planets = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
               swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO]
    planet_positions = {}

    # 計算每顆行星的位置
    for planet in planets:
        try:
            position, status = swe.calc_ut(jd, planet)
            if status < 0:  # 確保計算成功
                print(f"Error calculating {swe.get_planet_name(planet)}: status {status}")
                continue
            planet_name = swe.get_planet_name(planet)
            planet_positions[planet_name] = position[0]  # 獲取黃道經度
        except Exception as e:
            print(f"Exception while calculating {swe.get_planet_name(planet)}: {e}")

    return planet_positions
