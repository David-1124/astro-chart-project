def format_positions(positions):
    """格式化行星位置，轉為人類可讀格式"""
    formatted = []
    for planet, pos in positions.items():
        formatted.append(f"{planet}: 經度 {pos:.2f}°")
    return "\n".join(formatted)