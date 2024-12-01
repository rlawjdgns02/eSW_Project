from PIL import Image, ImageDraw
from Bubble import Bubble
from Joystick import Joystick
import time
import random
from Character import Character
from Board import create_bubbles, generate_random_map

# 랜덤 맵 생성
# map = generate_random_map()
map = [
        [".", ".", ".", ".", ".", ".", "B", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "/"],
        [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "/"],
        [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "/"],
        [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "/"],
        [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "/"]
    ]

print(map)

# 전역 변수

round_clear = False
fire = False
cur_bubble = None
nex_bubble = None
visited = []  # 방문한 버블
cannon = None
screen_width = 0
screen_height = 0
point = 0  # 점수


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


def create_bubble():
    """새로운 구슬 생성"""
    global cannon
    color = map_to_color(choice_color())
    angle = cannon.angle  # 대포의 각도를 구슬에 전달
    return Bubble(color=color, angle=angle, screen_size=(screen_width, screen_height), speed=5)

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



def prepare_bubbles():
    global cur_bubble, nex_bubble, cannon

    # 맵에 유효한 색상이 있는지 확인
    if all(cell in [".", "/"] for row in map for cell in row):
        round_clear = True
        return

    # 현재 버블과 다음 버블 생성
    if nex_bubble:
        cur_bubble = nex_bubble
    else:
        cur_bubble = create_bubble()
        
    nex_bubble = create_bubble()
    bubble_initial_y = cannon.center[1]
    cur_bubble.set_pos((screen_width // 2, bubble_initial_y))
    nex_bubble.set_pos((screen_width // 4, bubble_initial_y + 10))
    cur_bubble.set_angle(cannon.angle)  # 대포 각도를 구슬에 전달


def collision(down_cnt):
    global cur_bubble, fire, map, point
    if  cur_bubble is None:
        return

    # 맵 데이터 가져오기
    bubble_group = map  # map 데이터를 직접 사용
    if not bubble_group:
        return

    # 충돌
    hit_bubble = cur_bubble.overlap(bubble_group, down_cnt)
    if hit_bubble:
        x, y, direction = hit_bubble

        if y % 2 == 0:
            if direction == "right":
                bubble_group[y + 1][x] = get_color(cur_bubble.color)
                row_idx = y + 1
                col_idx = x
            else:
                bubble_group[y + 1][x - 1] = get_color(cur_bubble.color)
                row_idx = y + 1
                col_idx = x - 1
        else:
            if direction == "right":
                bubble_group[y + 1][x + 1] = get_color(cur_bubble.color)
                row_idx = y + 1
                col_idx = x + 1
            else:
                bubble_group[y + 1][x] = get_color(cur_bubble.color)
                row_idx = y + 1
                col_idx = x
                
        point += remove_bubbles(row_idx, col_idx, cur_bubble.color)
        print(f"{cur_bubble.color} attached at {cur_bubble.position}")
        print(map)
        
        cur_bubble = None
        fire = False
        map = bubble_group
        
        return point
        
    if cur_bubble.position[1] - cur_bubble.radius <= 0 + down_cnt * 20:
        x = int(list(cur_bubble.position)[0] // (cur_bubble.radius * 2))
        bubble_group[0][x] = get_color(cur_bubble.color)
        cur_bubble = None
        fire = False
        map = bubble_group
        return
    
def check_game_end(down_cnt):
    global map
    for col in range(9, -1, -1):  # 아래에서 위로 탐색
        # 해당 행에 색깔 있는 구슬이 있는지 확인
        if any(cell != "." and cell != "/" for cell in map[col]):
            # 색깔이 있는 구슬이 발견되면 해당 행만 검사
            for row in range(12):
                if map[col][row] != "." and map[col][row] != "/":  # 유효한 구슬만 리
                    other_y = col * 20 + 10 + down_cnt * 20  # 구슬의 중심 y 좌표
                    if other_y > 175:  # 기준 y 좌표를 초과하면 종료
                        return True
            break
    return False

def round_clear():
    global map
    
    # 맵의 모든 값을 확인
    for col in range(0, 10):  # 열
        for row in range(0, 12):  # 행
            if map[col][row] != "." and map[col][row] != "/":  # "." 또는 "/"가 아닐 경우
                return False  # 라운드 클리어 조건 실패

    return True  # 모든 값이 "." 또는 "/"일 경우


    

def remove_bubbles(row_idx, col_idx, color):
    visited.clear()
    visit(row_idx, col_idx, color)
    
    # 연결된 구슬이 3개 이상일 경우 제거
    if len(visited) >= 3:
        remove_visited_bubble()  # 연결된 구슬 제거
        plus = remove_gravity_bubble()  # 떠 있는 구슬 제거
        plus += len(visited)
        return plus * 50  # 점수 증가
    return 0  # 연결된 구슬이 없으면 점수 변화 없음
    

def visit(row_idx, col_idx, color=None):
    if row_idx < 0 or row_idx >= len(map) or col_idx < 0 or col_idx >= len(map[row_idx]):
        return

    if color and map[row_idx][col_idx] != get_color(color):
        return
    if map[row_idx][col_idx] in [".", "/"]:
        return
    
    if (row_idx, col_idx) in visited:
        return
    
    visited.append((row_idx, col_idx))
    
    if row_idx % 2 == 0:
        rows = [0, -1, -1, 0, 1, 1]
        cols = [-1, -1, 0, 1, 0, -1]
    else:
        rows = [0, -1, -1, 0, 1, 1]
        cols = [-1, 0, 1, 1, 1, 0]

    for i in range(len(rows)):
        visit(row_idx + rows[i], col_idx + cols[i], color)

def remove_visited_bubble():
    for x, y in visited:
        map[x][y] = "."

def remove_gravity_bubble():
    visited.clear()

    # 최상단 행에서 연결된 구슬들을 찾기
    for col_idx in range(12):
        if map[0][col_idx] != ".":
            visit(0, col_idx)
    
    cnt = 0
    
    # 연결되지 않은 구슬을 제거
    for row_idx in range(len(map)):
        for col_idx in range(len(map[row_idx])):
            if map[row_idx][col_idx] != "." and (row_idx, col_idx) not in visited:
                map[row_idx][col_idx] = "."
                cnt += 1
                
    return cnt
    

def reset_game():
    """게임 초기화 함수 - 새로운 라운드 시작"""
    global map, point, cur_bubble, nex_bubble

    # 맵 재생성
    map = generate_random_map()  # 새로운 맵 생성

    # 현재 및 다음 구슬 초기화
    cur_bubble = None
    nex_bubble = None

    # 화면에 새 맵을 렌더링 (필요 시 추가 로직 삽입)
    print("New round started! Map reset.")


def main():
    global cur_bubble, fire, map, cannon, screen_width, screen_height, point

    # 조이스틱 초기화
    joystick = Joystick()

    # LCD 화면 크기 설정
    screen_width = joystick.width
    screen_height = joystick.height

    # 대포 이미지 경로
    cannon_image_path = "/home/KimiHun/TA-ESW/project/drawable/pngwing.com.png"
    cannon = Character(screen_width, screen_height, image_path=cannon_image_path)
    
    # 벽 이미지 로드
    wall_image_path = "/home/KimiHun/TA-ESW/project/drawable/wall.png"
    wall = Image.open(wall_image_path).resize((screen_width, screen_height))
    
    # 배경 이미지 로드
    background_image_path = "/home/KimiHun/TA-ESW/project/drawable/spacebackground.png"
    background_image = Image.open(background_image_path).resize((screen_width, screen_height))

    # 디스플레이 초기화
    display_image = Image.new("RGB", (screen_width, screen_height))
    draw = ImageDraw.Draw(display_image)

    # 버블 맵 생성 및 초기화
    bubbles = create_bubbles(map, screen_width, screen_height)

    fire_cnt = 0
    round_cnt = 1
    down_cnt = 0
    print(cannon.center)
    
    # 메인 루프
    while True:
        # 조이스틱 명령 처리
        command = {'move': False, 'up_pressed': False, 'down_pressed': False, 'left_pressed': False, 'right_pressed': False}

        if not joystick.button_U.value:
            command['up_pressed'] = True
            command['move'] = True
        if not joystick.button_D.value:
            command['down_pressed'] = True
            command['move'] = True
        if not joystick.button_L.value:
            command['left_pressed'] = True
            command['move'] = True
        if not joystick.button_R.value:
            command['right_pressed'] = True
            command['move'] = True
        if not joystick.button_A.value:  # 발사 버튼
            if not fire:  # 발사 상태가 아닐 때만 발사
                fire = True
                cur_bubble.set_angle(cannon.angle)  # 발사 시점에서 대포의 각도 동기화
                fire_cnt += 1
                print(fire_cnt, down_cnt)
                
        # 배경 그리기
        display_image.paste(background_image, (0, 0))
        display_image.paste(wall, (0, -240 + down_cnt * 20))
        
        # 대포 각도 조정
        cannon.change_angle(command)

        # 충돌 처리
        collision(down_cnt)
        
        # 발사된 버블 처리
        if cur_bubble:
            nex_bubble.draw(display_image)
            if fire:
                cur_bubble.move()  # 구슬 이동
            cur_bubble.draw(display_image)  # 구슬 그리기
        else:
            prepare_bubbles()
        
        if fire_cnt % (8 - round_cnt) == 0 and fire_cnt != 0:
            down_cnt += 1
            fire_cnt = 0
            print(map)
            
        # 점수 표시
        draw.text((10, 210), f"Score: {point}", fill="red")
        
        if check_game_end(down_cnt):
            print("Game Over Detected!")  # 게임 종료 조건 로그
            draw.text((60, 120), "GAME IS OVER", fill="red")  # 게임 종료 메시지
            joystick.disp.image(display_image)  # 화면 갱신
            time.sleep(2)
            round_cnt = 1
            fire_cnt = 0
            down_cnt = 0
            point = 0
            reset_game()  # 게임 초기화
            continue  # 새 라운드로 넘어가기
            
        if round_clear():
            draw.text((60,120), "ROUND CLEAR", fill="red")
            joystick.disp.image(display_image)
            time.sleep(2)
            round_cnt += 1
            fire_cnt = 0
            down_cnt = 0
            reset_game()
            continue

        
        # 기존 버블 맵 그리기
        bubbles = create_bubbles(map, screen_width, screen_height)  # 매번 최신 상태로 bubbles 생성
        for bubble in bubbles:
            downed_position = (bubble["position"][0], bubble["position"][1] + down_cnt * 20)
            bubble_obj = Bubble(color=bubble["color"], position=downed_position)
            bubble_obj.draw(display_image)


        # 캐릭터(대포) 이미지 그리기
        if cannon.image:
            rotated_position = (
                int(cannon.center[0] - cannon.image.width / 2),
                int(cannon.center[1] - cannon.image.height / 2),
            )
            display_image.paste(cannon.image, rotated_position, cannon.image.convert("RGBA"))
        else:
            draw.ellipse(tuple(cannon.position), outline=cannon.outline, fill=(0, 0, 0))

        # 화살표(각도 표시) 그리기
        draw.line((cannon.center[0], cannon.center[1], cannon.arrow_end[0], cannon.arrow_end[1]), fill="blue", width=2)

        # LCD에 이미지 갱신
        joystick.disp.image(display_image)

        if fire_cnt % 5 == 0 and fire_cnt != 0:
            display_image.paste(wall, (0,-240 + fire_cnt // 5))

        # 프레임 제한
        time.sleep(0.001)

if __name__ == "__main__":
    main()
