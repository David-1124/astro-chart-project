import os
import numpy as np
import matplotlib.pyplot as plt
import swisseph as swe  # 需要 pyswisseph 用來計算天體位置與宮頭
from matplotlib.patches import Circle
from matplotlib import rcParams

rcParams['font.family'] = 'sans-serif'
# 先用支持特殊符號的字體，再用支持中文的字體作後備
rcParams['font.sans-serif'] = ['Segoe UI Symbol', 'Microsoft YaHei', 'DejaVu Sans','Microsoft JhengHei UI']
rcParams['axes.unicode_minus'] = False

# 依照 12 個星座的順序（此處定義 0-30° 為 Capricorn，即摩羯座）：
zodiac_signs = ['\u2648', '\u2649', '\u264A', '\u264B', '\u264C', '\u264D',
                '\u264E', '\u264F', '\u2650', '\u2651', '\u2652', '\u2653']
zodiac_names = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
               'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# 宮主星對應（僅作參考，實際運用可擴充）
ruling_planets = {
    'Aquarius': 'Uranus', 'Pisces': 'Neptune', 'Aries': 'Mars', 'Taurus': 'Venus',
    'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Pluto', 'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn'
}

# 行星符號
planet_symbols = {
    "Sun": "\u2609", "Moon": "\u263D", "Mercury": "\u263F",
    "Venus": "\u2640", "Mars": "\u2642", "Jupiter": "\u2643",
    "Saturn": "\u2644", "Uranus": "\u2645", "Neptune": "\u2646", "Pluto": "\u2647"
}

# 將行星名稱與 swisseph 常數對應
planet_codes = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO
}


def get_julian_day_with_time(year, month, day, hour, minute, second, timezone_offset):
    """
    根據客戶端輸入的當地出生時間及時區偏移量，
    將當地時間轉換為 UT 時間，並利用 swisseph 計算 Julian Day。
    """
    local_decimal = hour + minute / 60 + second / 3600
    ut_hour = local_decimal - timezone_offset
    return swe.julday(year, month, day, ut_hour)


def get_planet_positions(julian_day):
    """
    根據給定的 Julian Day，自動計算主要行星的黃道經度（單位：°）及逆行狀態。
    使用 FLG_SPEED 標記取得速度資訊，若黃道速度為負則視為逆行。

    回傳格式:
      { 'Sun': {'position': 123.45, 'retrograde': False, 'speed': 0.12}, ... }
    """
    positions = {}
    for planet, code in planet_codes.items():
        result = swe.calc(julian_day, code, swe.FLG_SWIEPH | swe.FLG_SPEED)
        pos = result[0][0] % 360
        speed = result[0][3] if len(result[0]) > 3 else 0
        retrograde = speed < 0
        positions[planet] = {'position': pos, 'retrograde': retrograde, 'speed': speed}
    return positions


def get_zodiac_sign(degree):
    """
    傳回某個度數所屬的星座及該星座內的度數，格式如 "Aries 10.25°"
    """
    index = int(degree // 30) % 12
    return f"{zodiac_names[index]} {degree % 30:.2f}°"


def calculate_house_cusps(julian_day, latitude, longitude):
    swe.set_topo(longitude, latitude, 0)
    cusps, ascmc = swe.houses(julian_day, latitude, longitude, b'A')
    return cusps



def get_house(degree, house_cusps):
    """
    根據行星的度數與宮頭，判斷該行星所在的宮位
    """
    for i in range(12):
        if i == 11:
            if house_cusps[i] <= degree or degree < house_cusps[0]:
                return i + 1
        else:
            if house_cusps[i] <= degree < house_cusps[i + 1]:
                return i + 1
    return 12


def calculate_aspects(planet_positions):
    """
    根據行星間角度，自動判斷主要相位（合相、六分相、四分相、拱相、對分）
    並傳回一個包含 (行星1, 行星2, 相位線顏色, 角度差) 的列表。
    """
    aspects_def = [
        (0, 8, 'purple'),
        (60, 6, 'green'),
        (90, 6, 'blue'),
        (120, 6, 'orange'),
        (180, 8, 'red')
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


def plot_natal_chart(planet_positions, julian_day, latitude, longitude, aspect_lines=None, output_path=None, show=True):
    """
    繪製命盤圖表，所有資訊都顯示在主圓內：
      - 黃道十二星座符號（調整至內部空白區）
      - 宮頭線及宮頭標記（顯示宮位數字與起始度數）
      - 行星位置、符號與逆行標記
      - 行星間主要相位線與精確角度標記
      - 右側資訊表格（行星名稱、星座度數、宮位）
      - 左側新增宮主星表格（宮位、星座度數、宮主星、飛入）
    """
    try:
        fig, ax = plt.subplots(figsize=(14, 10), subplot_kw={'projection': 'polar'})
        # 將 0° 定位在左側，角度依逆時針排列
        ax.set_theta_zero_location('W')
        ax.set_theta_direction(1)

        # 計算宮頭
        house_cusps = calculate_house_cusps(julian_day, latitude, longitude)
        ASC, MC = house_cusps[0], house_cusps[9]
        DSC, IC = (ASC + 180) % 360, (MC + 180) % 360

        # 調整：定義一個外圈半徑，所有文字標示都必須在此半徑內（例如 r=0.9）
        outer_r = 0.9

        # 繪製同心圓架構（例如從 0.4 到 outer_r）
        for r in [0.4, 0.5, 0.7, 0.8, outer_r]:
            ax.add_patch(Circle((0, 0), r, transform=ax.transData._b, color='gray', fill=False, linewidth=0.5))

        # 繪製黃道十二星座符號，將標示放在 (outer_r - 0.05)
        for i in range(12):
            theta_boundary = np.deg2rad(i * 30)
            # 畫出分隔線（這裡可調整在內圈）
            ax.plot([theta_boundary, theta_boundary], [outer_r - 0.2, outer_r - 0.05], color='gray', linewidth=1)
            mid_angle = np.deg2rad(i * 30 + 15)
            rotation = (i * 30 + 15) - 90
            ax.text(mid_angle, outer_r - 0.10, zodiac_signs[i],
                    ha='center', va='center', fontsize=18,
                    rotation=rotation, bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

        # 繪製宮頭標記（宮位數字與宮頭度數），放在 (outer_r - 0.45)
        for i, cusp in enumerate(house_cusps):
            theta = np.deg2rad(cusp)
            ax.text(theta, outer_r - 0.45, f"H{i + 1}\n{cusp:.1f}°", ha='center', va='center', fontsize=10,
                    color='black')

        # 繪製 ASC、MC、IC、DSC 線及標示，放在較內側（例如 r=0.8）
        for angle, label in zip([ASC, MC, IC, DSC], ["ASC", "MC", "IC", "DSC"]):
            theta = np.deg2rad(angle)
            ax.plot([theta, theta], [0.5, 0.8], color='gray', linestyle='-', linewidth=2.5)
            ax.text(theta, 0.85, label, ha='center', va='center', fontsize=12, color='red')

        # 若未傳入相位線，則自動計算相位（包含角度差）
        if aspect_lines is None:
            aspect_lines = calculate_aspects(planet_positions)

        # 繪製行星間的相位線及標示精確角度（以 r=0.4 為連線基準）
        for planet1, planet2, color, diff in aspect_lines:
            pos1 = planet_positions[planet1]['position']
            pos2 = planet_positions[planet2]['position']
            theta1 = np.deg2rad(pos1)
            theta2 = np.deg2rad(pos2)
            ax.plot([theta1, theta2], [0.4, 0.4], color=color, linestyle='-', linewidth=1)
            # 計算中點，注意極座標下的平均
            x = np.cos(theta1) + np.cos(theta2)
            y = np.sin(theta1) + np.sin(theta2)
            mid_angle = np.arctan2(y, x)
            if mid_angle < 0:
                mid_angle += 2 * np.pi
            ax.text(mid_angle, 0.3, f"{diff:.1f}°", ha='center', va='center', fontsize=10, color=color)

        # 繪製行星位置、符號及逆行標記（行星圖示放在 r=0.65）
        planet_data = []
        for planet, data in planet_positions.items():
            position = data['position']
            retrograde = data['retrograde']
            theta = np.deg2rad(position)
            ax.text(theta, 0.65, planet_symbols[planet], ha='center', va='center', fontsize=16)
            if retrograde:
                ax.text(theta, 0.68, "R", ha='center', va='center', fontsize=12, color='red')

            # 計算行星在所屬星座內的度數與對應星座符號
            # index 為該行星所在星座的索引（例如 0 表示 Capricorn）
            index = int(position // 30) % 12
            # 取得行星在該星座中的度數（0～30之間）
            degree_in_sign = position % 30
            # 從 zodiac_signs 取出對應的星座符號
            zodiac_symbol = zodiac_signs[index]
            # 組合顯示文字，例如 "♑10.3°"
            text = f"{zodiac_symbol}{degree_in_sign:.1f}°"
            # 計算文字的旋轉角度：
            rot = np.rad2deg(theta)
            if rot > 90:
                rot = rot - 180
            elif rot < -90:
                rot = rot + 180

            # 將這段文字顯示在行星符號下方（例如 r=0.5），並設定旋轉
            ax.text(theta, 0.55, text,
                    ha='center', va='center', fontsize=12, color='blue',
                    rotation=rot, rotation_mode='anchor')

            house = get_house(position, house_cusps)
            planet_name = f"{planet}{' R' if retrograde else ''}"
            planet_data.append([planet_name, get_zodiac_sign(position), house])

        # ===================== 新增部分：左側宮主星表格 =====================
        # 生成每一宮的資料，內容：宮位、星座及其度數、宮主星、飛入的宮位
        house_table_data = []
        for i, cusp in enumerate(house_cusps):
            house_num = i + 1
            # 依據宮頭落入的黃道，計算該宮頭所在星座的索引
            idx = int(cusp // 30) % 12
            # 計算該宮頭在所屬星座內的度數（0～30°）
            degree_in_sign = cusp % 30
            # 組合顯示文字：星座符號加上宮頭的完整黃經度數，例如 "♋183.0°"
            zodiac_text = f"{zodiac_signs[idx]}{cusp:.1f}°"
            # 取得該宮頭所在星座的名稱（例如 Capricorn、Aquarius 等）
            zodiac_name = zodiac_names[idx]
            # 根據該星座名稱，從 ruling_planets 取得宮主星
            ruling = ruling_planets[zodiac_name]
            # 用 planet_symbols 顯示宮主星符號（若有定義）
            ruling_symbol = planet_symbols[ruling] if ruling in planet_symbols else ruling
            # 飛入：取得該宮主星實際落入的宮位
            # 即從 planet_positions 中取得該宮主星的黃經位置，並利用 get_house() 計算其所在宮位
            flight_house = get_house(planet_positions[ruling]["position"], house_cusps)
            fei_text = f"H{flight_house}"
            house_table_data.append([house_num, zodiac_text, ruling_symbol, fei_text])

        left_column_labels = ["House", "Zodiac", "Ruling Planet", "H Location"]
        # 設定左側表格位置，這裡透過 bbox 的 x 值使用負值確保表格顯示在左側
        table_left = plt.table(
            cellText=house_table_data,
            colLabels=left_column_labels,
            loc='left',
            cellLoc='center',
            bbox=[-0.43, 0.65, 0.45, 0.5]
        )
        table_left.auto_set_font_size(False)
        table_left.set_fontsize(10)

        # =================================================================

        # 绘制行星位置、符号及逆行标记（行星图示放在 r=0.65）
        planet_data = []
        for planet, data in planet_positions.items():
            position = data['position']
            retrograde = data['retrograde']
            theta = np.deg2rad(position)
            # 绘制行星符号（图盘上仍以文字显示符号）
            ax.text(theta, 0.65, planet_symbols[planet], ha='center', va='center', fontsize=16)
            if retrograde:
                ax.text(theta, 0.68, "R", ha='center', va='center', fontsize=12, color='red')

            # ---------------------------
            # 修改右侧表格数据的构造：使用符号显示行星和星座
            # 对于 Planet 栏：直接使用行星符号（并附加逆行标记）
            p_symbol = planet_symbols[planet] + (" R" if retrograde else "")
            # 计算行星所在的星座索引及在该星座内的度数
            idx = int(position // 30) % 12
            degree_in_sign = position % 30
            # 对于 Zodiac (Degrees) 栏：以“星座符号 + 度数”的格式显示（例如 "♑22.7°"）
            z_symbol = f"{zodiac_signs[idx]}{degree_in_sign:.1f}°"
            # 取得行星所在的宫位
            house_val = get_house(position, house_cusps)
            # 构造数据列表：Planet、Zodiac (Degrees)、House
            planet_data.append([p_symbol, z_symbol, house_val])
            # ---------------------------
        # 绘制右侧行星信息表格
        column_labels = ["Planet", "Zodiac", "House"]
        table = plt.table(
            cellText=planet_data,
            colLabels=column_labels,
            loc='right',
            cellLoc='center',
            bbox=[1.0, 0.65, 0.35, 0.5]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)

        # 隱藏極座標刻度
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_title("Natal Chart", va='bottom', fontsize=16, pad=30)

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        if show:
            plt.show()
        else:
            plt.close(fig)
    except Exception as e:
        print(f"An error occurred while plotting the natal chart: {e}")


# -------------------------
# 測試與執行主程式
# -------------------------
# 輸入客戶端的完整出生資料（例如：1958 年 1 月 6 日，當地時間 12:00:00，台北 UTC+8）
birth_year = 1977
birth_month = 8
birth_day = 28
birth_hour = 22
birth_minute = 34
birth_second = 0
timezone_offset = 8  # 台北為 UTC+8

julian_day = get_julian_day_with_time(birth_year, birth_month, birth_day,
                                      birth_hour, birth_minute, birth_second,
                                      timezone_offset)

latitude, longitude = 25.033, 121.565

planet_positions = get_planet_positions(julian_day)

plot_natal_chart(planet_positions, julian_day, latitude, longitude,
                 aspect_lines=None, output_path="output/natal_chart.png", show=True)
