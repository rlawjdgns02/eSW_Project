from PIL import ImageDraw, Image
import math
import numpy as np

class Bubble:
    """버블 클래스"""
    def __init__(self, color, position=(0, 0), radius=10, angle=-90, screen_size=(800, 600), speed=5):
        self.color = color  # 구슬 색상
        self.position = position  # 초기 위치
        self.radius = radius  # 구슬 반지름
        self.state = "active"  # 구슬 상태 (active 또는 inactive)
        self.screen_width, self.screen_height = screen_size  # 화면 크기
        self.speed = speed  # 구슬 이동 속도
        self.set_angle(angle)  # 초기 각도 설정

        if self.color == 'red':
            self.image_path = "/home/KimiHun/TA-ESW/project/drawable/red.png"
            self.image = Image.open(self.image_path).resize((20, 20))
        elif self.color == 'yellow':
            self.image_path = "/home/KimiHun/TA-ESW/project/drawable/yellow.png"
            self.image = Image.open(self.image_path).resize((20, 20))
        elif self.color == 'blue':
            self.image_path = "/home/KimiHun/TA-ESW/project/drawable/blue.png"
            self.image = Image.open(self.image_path).resize((20, 20))
        elif self.color == 'purple':
            self.image_path = "/home/KimiHun/TA-ESW/project/drawable/pupple.png"
            self.image = Image.open(self.image_path).resize((20, 20))
        else:
            self.image_path = "/home/KimiHun/TA-ESW/project/drawable/green.png"
            self.image = Image.open(self.image_path).resize((20, 20))

    def draw(self, display_image):
        """버블을 화면에 그립니다."""
        if self.state == "active":
            x, y = self.position
            top_left_x = int(x - self.radius)
            top_left_y = int(y - self.radius)
            display_image.paste(self.image, (top_left_x, top_left_y), self.image)
            
    def move(self):
        """구슬 이동"""
        x, y = self.position

        # 이동 거리 계산 (속도와 각도)
        to_x = self.speed * math.cos(self.rad_angle)  # X축 이동량
        to_y = self.speed * math.sin(self.rad_angle)  # Y축 이동량

        # 위치 업데이트
        x += to_x
        y += to_y

        # 경계 충돌 처리 (벽 반사)
        if x - self.radius < 0:  # 왼쪽 벽에 닿은 경우
            x = self.radius  # 위치 조정
            self.set_angle(180 - self.angle)  # 각도 반사
        elif x + self.radius > self.screen_width:  # 오른쪽 벽에 닿은 경우
            x = self.screen_width - self.radius  # 위치 조정
            self.set_angle(180 - self.angle)  # 각도 반사

        # 위치 업데이트
        self.position = (x, y)

    def set_angle(self, angle):
        """구슬의 각도를 설정"""
        self.angle = angle % 360  # 각도를 0 ~ 360도로 제한
        self.rad_angle = math.radians(self.angle)  # 각도를 라디안으로 변환

    def set_pos(self, position):
        """구슬 위치를 설정"""
        self.position = position
    

    def overlap(self, bubble_group, down_cnt):
        x, y = self.position  # 현재 버블의 중심 좌표
        ego_radius = 10  # 현재 버블의 반지름

        for row_idx, row in enumerate(bubble_group):
            for col_idx, cell in enumerate(row):
                if cell in [".", "/"]:
                    continue

                # 다른 버블의 중심 좌표 계산
                other_x = col_idx * 20 + 10
                other_y = row_idx * 20 + 10 + down_cnt * 20

                # 홀수 행의 경우 x 좌표 조정
                if row_idx % 2 == 1:
                    other_x += 10

                # 두 원의 중심 거리 계산
                distance = math.sqrt((x - other_x) ** 2 + (y - other_y) ** 2)

                # 충돌 여부 확인
                if distance <= ego_radius + 10:  # 두 원의 반지름 합 비교
                    if x < other_x:
                        direction = "left"
                    else:
                        direction= "right"
                    return col_idx, row_idx, direction

        return None