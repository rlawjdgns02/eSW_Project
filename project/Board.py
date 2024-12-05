import random


def generate_random_map_row(row_idx):
    colors = ["R", "Y", "B", "G"]  # 사용 가능한 색상 목록
    row = []
    
    # 마지막에 '/' 추가 여부 결정
    append_slash = row_idx % 2 == 1  # 홀수 인덱스일 때만 추가
    
    for col_idx in range(11):  # 마지막 칸 제외한 11개 생성
        row.append(random.choice(colors + ["."]))
    
    if append_slash:
        row.append("/")  # 홀수 인덱스의 경우 마지막 칸에 '/' 추가
    else:
        row.append(random.choice(colors + ["."]))  # 짝수 인덱스는 랜덤

    return row

def generate_empty_row(row_idx):
    row = ["."] * 11  # 11개의 빈 칸
    if row_idx % 2 == 1:  # 홀수 인덱스일 경우 마지막 칸에 '/'
        row.append("/")
    else:
        row.append(".")  # 짝수 인덱스일 경우 '.' 유지
    return row

def generate_random_map():
    new_map = []
    
    # 첫 4줄은 랜덤으로 생성
    for row_idx in range(4):
        new_map.append(generate_random_map_row(row_idx))
    
    # 나머지 4줄은 빈 공간으로 채움
    for row_idx in range(4, 10):
        new_map.append(generate_empty_row(row_idx))

    return new_map

def create_bubble_array(map):
    bubbles = []
    color_map = {"R": "red", "Y": "yellow", "B": "blue", "G": "green", "W" : "black"}

    # 버블 크기 고정
    bubble_diameter = 20  # 직경(지름)을 10으로 설정
    bubble_radius = bubble_diameter // 2

    for row_idx, row in enumerate(map):
        for col_idx, cell in enumerate(row):
            if cell in [".", "/"]:
                continue
            x = col_idx * bubble_diameter + bubble_radius
            y = row_idx * bubble_diameter + bubble_radius
            if row_idx % 2 == 1:  # 홀수 행의 오프셋 적용
                x += bubble_radius
            color = color_map.get(cell, "white")
            bubbles.append({
                "color": color,
                "position": (x, y),
                "radius": bubble_radius,
            })

    return bubbles

map = generate_random_map()
