from PIL import Image
import numpy as np
import math

class Character:
    def __init__(self, width, height, image_path=None):
        self.position = np.array([width / 2 - 15, height - 30, width / 2 + 15, height])
        self.center = np.array([(self.position[0] + self.position[2]) / 2, (self.position[1] + self.position[3]) / 2])
        self.angle = -90  # 초기 각도
        self.arrow_end = self.center
        self.arrow_length = 50

        # 이미지 불러오기 및 크기 조정
        if image_path:
            try:
                self.original_image = Image.open(image_path).resize(
                    (int(self.position[2] - self.position[0]), int(self.position[3] - self.position[1]))
                )
                self.image = self.original_image.rotate(0, expand=True)
            except FileNotFoundError:
                print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
                self.image = None
        else:
            self.image = None

    def change_angle(self, command=None):
        # 입력에 따라 각도 조정
        if command and command['move']:
            if command['left_pressed']:
                if self.angle > -180:
                    self.angle -= 5
            if command['right_pressed']:
                if self.angle < 0:
                    self.angle += 5

            
            # 이미지 회전
            if self.image:
                self.image = self.original_image.rotate(-self.angle - 90, expand=True)

        # 화살표 방향 계산
        self.arrow_end = self.get_arrow_direction(self.angle, self.arrow_length)

    def get_arrow_direction(self, angle, length):
        # 화살표 끝 좌표 계산
        end_x = self.center[0] + length * math.cos(math.radians(angle))
        end_y = self.center[1] + length * math.sin(math.radians(angle))
        return np.array([end_x, end_y])