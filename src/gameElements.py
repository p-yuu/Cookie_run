import random

import pygame

import config
from config import BUFF, CLOCK, DEBUFF, FLYING, FPS, LARGE_OBT, SCREEN, SMALL_OBT, WIDTH


class Buff(pygame.sprite.Sprite):
    def __init__(self, kind):
        pygame.sprite.Sprite.__init__(self)

        if kind == "speed_up":
            self.image = BUFF
            self.effect = 3
        elif kind == "speed_down":
            self.image = DEBUFF
            self.effect = -2

        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = random.choice([150, 355])

    def update(self):
        self.rect.x -= config.game_speed
        if self.rect.right <= 0:
            self.kill()

    def get_effect(self):
        return self.effect


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, images, y, kind, idx):
        pygame.sprite.Sprite.__init__(self)

        self.image = images
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = y
        self.index = idx  # for json
        self.kind = kind  # for json

    def update(self):
        self.rect.x -= config.game_speed
        if self.rect.right <= 0:
            self.kill()


def Small_OBT():
    idx = random.randint(0, 2)
    return Obstacle(SMALL_OBT[idx], 320, "small", idx)


def Large_OBT():
    idx = random.randint(0, 2)
    return Obstacle(LARGE_OBT[idx], 265, "large", idx)


def Fly_OBT():
    return Obstacle(FLYING, 190, "fly", 0)


def hide_obstacle():  # 隱藏障礙物
    config.obstacle_hidden = True
    config.obstacle_time = pygame.time.get_ticks()
    config.obstacle_group.empty()  # 清空畫面上的障礙物
    config.buff_group.empty()


def get_last_x():  # 取得最右物件
    xs = []
    for s in config.obstacle_group:
        xs.append(s.rect.right)
    for s in config.buff_group:
        xs.append(s.rect.right)
    return max(xs) if xs else 0


if __name__ == "__main__":
    config.game_speed = 10
    buff_count = 0
    config.obstacle_group = pygame.sprite.Group()
    config.buff_group = pygame.sprite.Group()

    run = True
    while run:
        CLOCK.tick(FPS)
        # ---------- 取得輸入 ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # ---------- 更新遊戲 ----------
        config.obstacle_group.update()
        config.buff_group.update()

        if get_last_x() < WIDTH - random.randint(550, 650):
            r = random.randint(0, 5)
            if r == 0 or (buff_count >= 2 and r == 3):
                config.obstacle_group.add(Small_OBT())
                buff_count = 0
            elif r == 1 or (buff_count >= 2 and r == 4):
                config.obstacle_group.add(Large_OBT())
                buff_count = 0
            elif r == 2:
                config.obstacle_group.add(Fly_OBT())
                buff_count = 0
            elif r == 3:
                config.buff_group.add(Buff("speed_up"))
                buff_count += 1
            elif r == 4:
                config.buff_group.add(Buff("speed_down"))
                buff_count += 1
        # ---------- 畫面顯示 ----------
        SCREEN.fill((255, 255, 255))
        config.obstacle_group.draw(SCREEN)
        config.buff_group.draw(SCREEN)
        pygame.display.update()
    pygame.quit()
