import os
import numpy as np
import matplotlib.pyplot as plt
import swisseph as swe  # 需要 pyswisseph 用来计算天体位置与宫头
from matplotlib.patches import Circle
from matplotlib import rcParams

rcParams['font.family'] = 'sans-serif'
# 先用支持特殊符号的字体，再用支持中文的字体作后备
rcParams['font.sans-serif'] = ['Segoe UI Symbol', 'Microsoft YaHei', 'DejaVu Sans', 'Microsoft JhengHei UI']
rcParams['axes.unicode_minus'] = False

# 定义 12 个星座的符号和名称（这里采用常见的黄道顺序：从 Aries 开始）
zodiac_signs = ['\u2648', '\u2649', '\u264A', '\u264B', '\u264C', '\u264D',
                '\u264E', '\u264F', '\u2650', '\u2651', '\u2652', '\u2653']
zodiac_names = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# 定义每个星座对应的颜色（你可以根据喜好调整颜色值）
zodiac_colors = {
    'Aries': '#FF5733',
    'Taurus': '#FFC300',
    'Gemini': '#DAF7A6',
    'Cancer': '#C70039',
    'Leo': '#900C3F',
    'Virgo': '#581845',
    'Libra': '#2E86C1',
    'Scorpio': '#1ABC9C',
    'Sagittarius': '#F39C12',
    'Capricorn': '#7D3C98',
    'Aquarius': '#3498DB',
    'Pisces': '#5DADE2'
}

# 宫主星对应（仅作参考，实际运用可扩充）
ruling_planets = {
    'Aquarius': 'Uranus', 'Pisces': 'Neptune', 'Aries': 'Mars', 'Taurus': 'Venus',
    'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Pluto', 'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn'
}

# 行星符号
planet_symbols = {
    "Sun": "\u2609", "Moon": "\u263D", "Mercury": "\u263F",
    "Venus": "\u2640", "Mars": "\u2642", "Jupiter": "\u2643",
    "Saturn": "\u2644", "Uranus": "\u2645", "Neptune": "\u2646", "Pluto": "\u2647"
}

# 将行星名称与 swisseph 常数对应
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
    根据客户端输入的当地出生时间及时区偏移量，
    将当地时间转换为 UT 时间，并利用 swisseph 计算 Julian Day。
    """
    local_decimal = hour + minute / 60 + second / 3600
    ut_hour = local_decimal - timezone_offset
    return swe.julday(year, month, day, ut_hour)


def get_planet_positions(julian_day):
    """
    根据给定的 Julian Day，自动计算主要行星的黄道经度（单位：°）及逆行状态。
    使用 FLG_SPEED 标记获取速度信息，若黄道速度为负则视为逆行。

    返回格式:
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
    返回某个度数所属的星座及该星座内的度数，格式如 "Aries 10.25°"
    """
    index = int(degree // 30) % 12
    return f"{zodiac_names[index]} {degree % 30:.2f}°"


def calculate_house_cusps(julian_day, latitude, longitude):
    swe.set_topo(longitude, latitude, 0)
    # 使用 "P" 表示 Placidus 宫位系统（以字节串形式）
    cusps, ascmc = swe.houses(julian_day, latitude, longitude, b"P")
    return cusps


def get_house(degree, house_cusps):
    """
    根据行星的度数与宫头，判断该行星所在的宫位
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
    根据行星间角度，自动判断主要及辅助相位，并返回一个包含
    (行星1, 行星2, 相位线颜色, 实际角度差, 标准相位角) 的列表。
    新增相位包括：
      - 半六分相：30° (orb 3°, 颜色 "magenta")
      - 半方相：45° (orb 3°, 颜色 "cyan")
      - 七分相：约51.43° (orb 3°, 颜色 "olive")
      - 五分相：72° (orb 3°, 颜色 "teal")
      - 补充半方相：135° (orb 3°, 颜色 "pink")
      - 双五分相：144° (orb 3°, 颜色 "brown")
      - 欠刑相：150° (orb 3°, 颜色 "gray")
    """
    aspects_def = [
        (0, 8, 'purple'),
        (30, 3, 'magenta'),
        (45, 3, 'cyan'),
        (51.43, 3, 'olive'),
        (60, 6, 'green'),
        (72, 3, 'teal'),
        (90, 6, 'blue'),
        (120, 6, 'orange'),
        (135, 3, 'pink'),
        (144, 3, 'brown'),
        (150, 3, 'gray'),
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
            best = None
            best_error = None
            for aspect_angle, orb, color in aspects_def:
                error = abs(diff - aspect_angle)
                if error <= orb:
                    if best_error is None or error < best_error:
                        best = (aspect_angle, color)
                        best_error = error
            if best is not None:
                aspect_angle, color = best
                aspect_lines.append((planets[i], planets[j], color, diff, aspect_angle))
    return aspect_lines


def plot_natal_chart(planet_positions, julian_day, latitude, longitude, aspect_lines=None, output_path=None, show=True):
    """
    绘制命盘图表，所有信息都显示在主圆内：
      - 外圈星座符号及分界线：根据实际宫头数据绘制，在每个宫头线上显示对应星座符号及宫位起始点的黄经，
        转换为星座+度分格式（例如 "♑25°30′"）
      - 宫头标记：显示宫位编号（仅显示数字 1～12），位置为当前宫头与下一宫头之间的中点
      - ASC、MC、IC、DSC 线及标示
      - 行星位置、符号及逆行标记与黄经文本：在行星所在直线上依次显示行星符号和黄经文本，
        黄经文本为星座内的度分格式（例如 "25.3° ♑"），且避免重叠
      - 右侧信息表格（行星以符号、星座及度分、宫位）
      - 左侧宫主星表格（House, Zodiac (House start), Ruling Planet, H Location）
    """
    global planet_data
    try:
        fig, ax = plt.subplots(figsize=(14, 10), subplot_kw={'projection': 'polar'})
        ax.set_theta_zero_location('W')
        ax.set_theta_direction(1)

        # 计算宫头（Placidus 系统返回的 12 个宫头黄经值）
        house_cusps = calculate_house_cusps(julian_day, latitude, longitude)
        # 设定偏移量，将 ASC 固定为 0°，以第一个宫头为基准
        offset = house_cusps[0]

        # 定义辅助函数：将角度转换为相对于 ASC 的角度（单位：度）
        def trans(angle):
            return (angle - offset) % 360

        # 计算主要点（转换后的角度）
        ASC = trans(house_cusps[0])  # 应为 0
        MC = trans(house_cusps[9])
        DSC = (ASC + 180) % 360
        IC = (MC + 180) % 360

        outer_r = 0.9

        # 绘制同心圆架构（例如从 0.4 到 outer_r）
        for r in [0.4, 0.5, 0.7, 0.8, outer_r]:
            ax.add_patch(Circle((0, 0), r, transform=ax.transData._b,
                                color='gray', fill=False, linewidth=0.5))

        # —— 绘制外圈星座符号及分界线 ——
        # 在每个宫头线上显示对应星座符号及宫位起始点的黄经转换为星座内度分格式
        for i in range(12):
            cusp_current = house_cusps[i]
            theta_boundary = np.deg2rad(trans(cusp_current))
            ax.plot([theta_boundary, theta_boundary], [outer_r - 0.2, outer_r - 0.05],
                    color='gray', linewidth=1)
            idx = int(cusp_current // 30) % 12
            # 计算宫内度数：内部度数 = cusp_current - (idx * 30)
            internal = cusp_current - (idx * 30)
            d = int(internal)
            m = int(round((internal - d) * 60))
            zodiac_text = f"{zodiac_signs[idx]}{d}°{m}′"
            # 使用对应星座颜色
            color_zodiac = zodiac_colors[zodiac_names[idx]]
            ax.text(theta_boundary, outer_r - 0.10, zodiac_text,
                    ha='center', va='center', fontsize=12, color=color_zodiac,
                    rotation=0, rotation_mode='anchor',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

        # —— 绘制宫头标记 ——
        # 显示宫位编号（1～12），位置为当前宫头与下一宫头之间的中点
        for i in range(12):
            cusp_current = house_cusps[i]
            cusp_next = house_cusps[(i + 1) % 12]
            current = trans(cusp_current)
            nxt = trans(cusp_next)
            if nxt < current:
                nxt += 360
            mid_deg = (current + nxt) / 2.0 % 360
            theta_mid = np.deg2rad(mid_deg)
            ax.text(theta_mid, outer_r - 0.45, f"{i + 1}",
                    ha='center', va='center', fontsize=10, color='brown')

        # —— 绘制 ASC、MC、IC、DSC 线及标示 ——
        for angle, label in zip([ASC, MC, IC, DSC], ["ASC", "MC", "IC", "DSC"]):
            theta = np.deg2rad(angle)
            ax.plot([theta, theta], [0.5, 0.8], color='gray', linestyle='-', linewidth=2.5)
            ax.text(theta, 0.85, label, ha='center', va='center', fontsize=12, color='red')

        # —— 绘制行星间相位线及标示精确相位符号 ——
        # 定义相位符号映射字典
        aspect_symbol_map = {
            0: "*",  # 合相
            30: "◦",  # 半六分相
            45: "▢",  # 半方相
            51.43: "✶",  # 七分相
            60: "∿",  # 六分相
            72: "⌘",  # 五分相
            90: "□",  # 四分相
            120: "△",  # 拱相
            135: "⊟",  # Sesquisquare
            144: "✹",  # 双五分相
            150: "⁑",  # 欠刑相/Quincunx
            180: "⊥"  # 对分相
        }
        if aspect_lines is None:
            aspect_lines = calculate_aspects(planet_positions)
        for aspect_data in aspect_lines:
            if len(aspect_data) == 4:
                planet1, planet2, color, diff = aspect_data
                aspect_angle = 0
            else:
                planet1, planet2, color, diff, aspect_angle = aspect_data
            pos1 = planet_positions[planet1]['position']
            pos2 = planet_positions[planet2]['position']
            theta1 = np.deg2rad(trans(pos1))
            theta2 = np.deg2rad(trans(pos2))
            ax.plot([theta1, theta2], [0.4, 0.4], color=color, linestyle='-', linewidth=1)
            # 计算在半径为 0.4 处两个端点的笛卡尔坐标，并取中点
            r_line = 0.4
            x1, y1 = r_line * np.cos(theta1), r_line * np.sin(theta1)
            x2, y2 = r_line * np.cos(theta2), r_line * np.sin(theta2)
            x_mid = (x1 + x2) / 2.0
            y_mid = (y1 + y2) / 2.0
            r_mid = np.sqrt(x_mid ** 2 + y_mid ** 2)
            theta_mid = np.arctan2(y_mid, x_mid)
            if theta_mid < 0:
                theta_mid += 2 * np.pi
            # 采用“最接近法”取得相位标准角的映射
            rounded_aspect = min(aspect_symbol_map.keys(), key=lambda x: abs(x - aspect_angle))
            symbol = aspect_symbol_map.get(rounded_aspect, "")
            ax.text(theta_mid, r_mid, symbol, ha='center', va='center', fontsize=14, color=color)

        # —— 绘制行星位置、符号及逆行标记与黄经文本 ——
        planet_data = []
        used_planet_angles = []  # 用于记录行星符号显示的角度（单位：度），避免重叠
        used_text_angles = []  # 用于记录黄经文本显示的角度（单位：度），避免重叠
        for planet, data in planet_positions.items():
            pos = data['position']
            retrograde = data['retrograde']
            # 计算基准角度（相对于 ASC），单位为度
            base_angle_deg = trans(pos)

            # 避免行星符号重叠：调整行星符号显示角度
            planet_angle_deg = base_angle_deg
            threshold = 3  # 阈值设为 3 度（可根据需要调整）
            while any(abs(planet_angle_deg - used) < threshold for used in used_planet_angles):
                planet_angle_deg = (planet_angle_deg + threshold) % 360
            used_planet_angles.append(planet_angle_deg)
            theta_planet = np.deg2rad(planet_angle_deg)
            ax.text(theta_planet, 0.65, planet_symbols[planet],
                    ha='center', va='center', fontsize=16, color='black')
            if retrograde:
                ax.text(theta_planet, 0.68, "R", ha='center', va='center', fontsize=12, color='red')

            # 计算行星黄经转换为该星座内的度数：
            idx = int(pos // 30) % 12
            degree_in_sign = pos % 30
            # 构造文本：依原设定，将星座符号和度数分开显示
            # 保持原来的格式，如 "♑" 和 "25.3°"
            zodiac_text = zodiac_signs[idx]
            degree_text = f"{degree_in_sign:.1f}°"

            # 避免黄经文本重叠：调整文本显示角度（单位：度）
            text_angle_deg = base_angle_deg
            while any(abs(text_angle_deg - used) < threshold for used in used_text_angles):
                text_angle_deg = (text_angle_deg + threshold) % 360
            used_text_angles.append(text_angle_deg)
            theta_text = np.deg2rad(text_angle_deg)
            # 定义旋转角度，使文本随弧线排列：这里可以直接用 theta_text 转换而不固定为水平
            rot = np.rad2deg(theta_text) - 90
            ax.text(theta_text, 0.59, degree_text,
                    ha='center', va='center', fontsize=12, color=zodiac_colors[zodiac_names[idx]],
                    rotation=0, rotation_mode='anchor')
            ax.text(theta_text, 0.53, zodiac_text,
                    ha='center', va='center', fontsize=12, color=zodiac_colors[zodiac_names[idx]],
                    rotation=0, rotation_mode='anchor')

            house_val = get_house(pos, house_cusps)
            p_symbol = planet_symbols[planet] + (" R" if retrograde else "")
            planet_data.append([p_symbol, f"{zodiac_text} {degree_text}", house_val])

        # —— 绘制左侧宫主星表格 ——
        house_table_data = []
        for i, cusp in enumerate(house_cusps):
            house_num = i + 1
            idx = int(cusp // 30) % 12
            internal = cusp - (idx * 30)
            d = int(internal)
            m = int(round((internal - d) * 60))
            zodiac_text = f"{zodiac_signs[idx]}{d}°{m}′"
            zodiac_name = zodiac_names[idx]
            ruling = ruling_planets[zodiac_name]
            ruling_symbol = planet_symbols[ruling] if ruling in planet_symbols else ruling
            flight_house = get_house(planet_positions[ruling]["position"], house_cusps)
            fei_text = f"H{flight_house}"
            house_table_data.append([house_num, zodiac_text, ruling_symbol, fei_text])

        left_column_labels = ["House", "Zodiac", "Ruling Planet", "H Location"]
        table_left = plt.table(
            cellText=house_table_data,
            colLabels=left_column_labels,
            loc='left',
            cellLoc='center',
            bbox=[-0.43, 0.65, 0.45, 0.5]
        )
        table_left.auto_set_font_size(False)
        table_left.set_fontsize(10)

        # —— 绘制右侧行星信息表格 ——
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
# 测试与执行主程序
# -------------------------
if __name__ == "__main__":
    # 输入客户端的完整出生资料（例如：1967 年 11 月 18 日，当地时间 10:55:00，台北 UTC+8）
    birth_year = 1975
    birth_month = 7
    birth_day = 13
    birth_hour = 19
    birth_minute = 20
    birth_second = 0
    timezone_offset = 8  # 台北为 UTC+8

    # 例如使用台北的经纬度
    latitude, longitude = 37.61667, 55.75

    julian_day = get_julian_day_with_time(birth_year, birth_month, birth_day,
                                          birth_hour, birth_minute, birth_second,
                                          timezone_offset)

    planet_positions = get_planet_positions(julian_day)

    plot_natal_chart(planet_positions, julian_day, latitude, longitude,
                     aspect_lines=None, output_path="output/natal_chart.png", show=True)
