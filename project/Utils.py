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

def map_to_color(code):
    color_map = {
        "R": "red",
        "Y": "yellow",
        "B": "blue",
        "G": "green"
    }
    return color_map.get(code, "black")

def choice_color():
    colors = []
    for row in map:
        for col in row:
            if col not in colors and col not in [".", "/"]:  # 유효한 색상만 추가
                colors.append(col)

    if not colors:  # colors가 비어 있는 경우 기본값 처리
        print("No valid colors left in the map. Using default color.")
        return "R"  # 기본 색상 (예: 빨강)

    return random.choice(colors)


def check_game_end(map, down_cnt):
    for col in range(9, -1, -1):  # 아래에서 위로 탐색
        # 해당 행에 색깔 있는 구슬이 있는지 확인
        if any(cell != "." and cell != "/" for cell in map[col]):
            other_y = col * 20 + 10 + down_cnt * 20  # 구슬의 중심 y 좌표
            if other_y > 175:  # 기준 y 좌표를 초과하면 종료
                return True
    return False

def round_clear(map):
    
    # 맵의 모든 값을 확인
    for col in range(0, 10):  # 열
        for row in range(0, 12):  # 행
            if map[col][row] != "." and map[col][row] != "/":  # "." 또는 "/"가 아닐 경우
                return False  # 라운드 클리어 조건 실패

    return True  # 모든 값이 "." 또는 "/"일 경우

def reset_game(cur_bubble, nex_bubble):
    # 맵 재생성
    map = generate_random_map()  # 새로운 맵 생성

    # 현재 및 다음 구슬 초기화
    cur_bubble = None
    nex_bubble = None

    print("New round started! Map reset.")
    return map