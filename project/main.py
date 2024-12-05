from PIL import Image, ImageDraw, ImageFont
from Bubble import Bubble, create_bomb, create_bubble
from Joystick import Joystick
import time
from Character import Character
from Board import create_bubble_array, map
from Utils import get_color, reset_game, round_clear, check_game_end


# 전역 변수
fire = False
suc_cnt = 0
cur_bubble = None
nex_bubble = None
visited = []  # 방문한 버블을 나타내기 위한 리스트
cannon = None
screen_width = 0
screen_height = 0
point = 0  # 점수

def prepare_bubbles():
    global cur_bubble, nex_bubble, cannon, suc_cnt, map

    # 맵에 유효한 색상이 있는지 확인
    if all(cell in [".", "/"] for row in map for cell in row):
        return

    # 현재 버블과 다음 버블 생성
    if nex_bubble:
        cur_bubble = nex_bubble
    else:
        cur_bubble = create_bubble(cannon, screen_width, screen_height, map)
    
    if suc_cnt >= 10:
        nex_bubble = create_bomb(cannon, screen_width, screen_height)
        suc_cnt = 0
    else:
        nex_bubble = create_bubble(cannon, screen_width, screen_height, map)
        
    bubble_initial_y = cannon.center[1]
    cur_bubble.set_pos((screen_width // 2, bubble_initial_y))
    nex_bubble.set_pos((screen_width // 4, bubble_initial_y + 10))
    cur_bubble.set_angle(cannon.angle)  # 대포 각도를 구슬에 전달


def collision(down_cnt):
    global cur_bubble, fire, map, point
    if  cur_bubble is None:
        return

    # 맵 정보 가져오기
    bubble_group = map  # map 정보를 직접 사용
    if not bubble_group:
        return

    # 충돌 감지 및 반영
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
                
        if cur_bubble.color == "black":
            point += remove_bomb_bubble(row_idx, col_idx)
        
        else:
            point += remove_bubbles(row_idx, col_idx, cur_bubble.color)
        print(f"{cur_bubble.color} attached at {cur_bubble.position}")
        
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

def remove_bubbles(row_idx, col_idx, color):
    global suc_cnt
    visited.clear()
    visit(row_idx, col_idx, color)
    
    # 연결된 구슬이 3개 이상일 경우 제거
    if len(visited) >= 3:
        suc_cnt += len(visited)
        plus = len(visited)
        remove_visited_bubble()  # 연결된 구슬 제거
        plus += remove_gravity_bubble()  # 떠 있는 구슬 제거
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

def remove_bomb_bubble(row_idx, col_idx):
    global map
    bomb_cnt = 0
    if row_idx % 2 == 0:
        rem = [[-1, -1], [-1, 0], [0, -1], [0, 1], [1, -1], [1, 0]]
    else:
        rem = [[-1, 0], [-1, 1], [0, -1], [0, 1], [1, 0], [1, 1]]
    
    for row, col in rem:
        x, y = row_idx + row, col_idx + col  # 상대 좌표를 절대 좌표로 변환
        if 0 <= x < len(map) and 0 <= y < len(map[0]):  # 맵 경계를 초과하지 않도록 확인
            if map[x][y] not in [".", "/"]:  # 유효한 버블인지 확인
                map[x][y] = "."  # 해당 위치 버블 제거
                bomb_cnt += 1
    map[row_idx][col_idx] = "."
    remove_gravity_bubble()

    return bomb_cnt * 50  # 점수를 반환



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
    font_path = "/home/KimiHun/TA-ESW/project/drawable/FontBold.ttf"
    font_forGame = ImageFont.truetype(font_path, 25)
    font_forPoint = ImageFont.truetype(font_path, 15)

    # 버블 맵 생성 및 초기화
    bubbles = create_bubble_array(map)

    fire_cnt = 0
    round_cnt = 1
    down_cnt = 0
    
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

        # 배경 그리기
        display_image.paste(background_image, (0, 0))
        display_image.paste(wall, (0, -240 + down_cnt * 20))
        
        # 대포 각도 조정
        cannon.change_angle(command)

        # 충돌 처리
        collision(down_cnt)
        
        # 캐릭터(대포) 이미지 그리기
        if cannon.image:
            rotated_position = (
                int(cannon.center[0] - cannon.image.width / 2),
                int(cannon.center[1] - cannon.image.height / 2),
            )
            display_image.paste(cannon.image, rotated_position, cannon.image.convert("RGBA"))
        else:
            draw.ellipse(tuple(cannon.position), outline=cannon.outline, fill=(0, 0, 0))
        
        # 발사된 버블 처리
        if cur_bubble:
            nex_bubble.draw(display_image)
            if fire:
                cur_bubble.move()  # 구슬 이동
            cur_bubble.draw(display_image)  # 구슬 그리기
        else:
            prepare_bubbles()
        
        if fire_cnt % (10 - round_cnt) == 0 and fire_cnt != 0:
            down_cnt += 1
            display_image.paste(wall, (0,-240 + down_cnt*20))
            fire_cnt = 0
            
        
        if check_game_end(map, down_cnt):
            draw.text((20, 80), "GAME OVER", fill="red", font = font_forGame)  # 게임 종료 메시지
            draw.text((20, 120), "GO TO NEW GAME?", fill="blue", font = font_forPoint)
            draw.text((20, 140), "PRESS B BUTTON", fill="red", font = font_forPoint)
            draw.text((20, 170), f"FINAL SCORE: {point}", fill="red", font = font_forPoint)
            joystick.disp.image(display_image)  # 화면 갱신
            while not joystick.button_B.value:
                round_cnt = 1
                fire_cnt = 0
                down_cnt = 0
                suc_cnt = 0
                point = 0
                map = reset_game(cur_bubble, nex_bubble)
                time.sleep(0.1)
            continue  # 새 라운드로 넘어가기
        else:
            draw.text((10, 210), f"Score: {point}", fill="red", font = font_forPoint)

            
        if round_clear(map):
            draw.text((10,80), "ROUND CLEAR", fill="red", font = font_forGame)
            draw.text((20, 120), "GO TO NEXT ROUND?", fill="blue", font = font_forPoint)
            draw.text((20, 140), "PRESS B BUTTON", fill="red", font = font_forPoint)
            joystick.disp.image(display_image)
            while not joystick.button_B.value:
                round_cnt += 1
                fire_cnt = 0
                down_cnt = 0
                suc_cnt = 0
                map = reset_game(cur_bubble, nex_bubble)
                time.sleep(0.1)
            continue

        
        # 기존 버블 맵 그리기
        bubbles = create_bubble_array(map)  # 매번 최신 상태로 bubbles 생성
        for bubble in bubbles:
            downed_position = (bubble["position"][0], bubble["position"][1] + down_cnt * 20)
            bubble_obj = Bubble(color=bubble["color"], position=downed_position)
            bubble_obj.draw(display_image)


        # 화살표(각도 표시) 그리기
        draw.line((cannon.center[0], cannon.center[1], cannon.arrow_end[0], cannon.arrow_end[1]), fill="blue", width=2)
        draw.line((0, 185, screen_width, 185), fill="red", width=2)

        # LCD에 이미지 갱신
        joystick.disp.image(display_image)

        # 프레임 제한
        time.sleep(0.001)

if __name__ == "__main__":
    main()
