import pygame
import random
import config
from config import WIDTH, SMALL_OBT, LARGE_OBT, FLYING

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, images, y, kind, idx):
        pygame.sprite.Sprite.__init__(self)

        self.image = images
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = y
        self.index = idx # for json
        self.kind = kind # for json

    def update(self):
        self.rect.x -= config.game_speed
        if self.rect.right <= 0:
            self.kill()

def Small_OBT():
    idx = random.randint(0,2)
    return Obstacle(SMALL_OBT[idx], 320, "small", idx)

def Large_OBT():
    idx = random.randint(0,2)
    return Obstacle(LARGE_OBT[idx], 265, "large", idx)

def Fly_OBT():
    return Obstacle(FLYING, 190, "fly", 0)

def hide_obstacle(): # 隱藏障礙物
    config.obstacle_hidden = True
    config.obstacle_time = pygame.time.get_ticks()
    config.obstacle_group.empty() # 清空畫面上的障礙物
    config.buff_group.empty()

def get_last_x(): #取得最右物件
    xs = []
    for s in config.obstacle_group:
        xs.append(s.rect.right)
    for s in config.buff_group:
        xs.append(s.rect.right)
    return max(xs) if xs else 0