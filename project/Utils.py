import random
from Board import map, generate_random_map

def get_color(color):
    if color == "red":
        return "R"
    elif color == "yellow":
        return "Y"
    elif color == "blue":
        return "B"
    elif color == "green":
        return "G"
    elif color == "purple":
        return "P"

def map_to_color(code):
    color_map = {
        "R": "red",
        "Y": "yellow",
        "B": "blue",
        "G": "green",
        "P": "purple"
    }
    return color_map.get(code, "black")

def choice_color():
    colors = []
    for row in map:  # 기존 map -> game_map
        for col in row:
            if col not in colors and col not in [".", "/"]:  # 유효한 색상만 추가
                colors.append(col)

    if not colors:  # colors가 비어 있는 경우 기본값 처리
        print("No valid colors left in the map. Using default color.")
        return "R"  # 기본 색상 (예: 빨강)

    return random.choice(colors)
