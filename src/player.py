import pygame
from config import HIDE, JUMPING, RUNNING, SLIDING


class Player(pygame.sprite.Sprite):
    X_POS = 80
    Y_POS = 310
    Y_POS_SLIDE = 338
    JUMP_VEL = 16
    ANIM_STEP = 10  # 多少幀一張

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.slide_img = SLIDING

        self.is_run = True
        self.is_jump = False
        self.is_slide = False

        self.step_idx = 0  # 步驟索引
        self.jump_vel = self.JUMP_VEL
        self.jump_time = 2
        self.on_ground = True

        self.lives = 3
        self.hidden = False
        self.hide_time = 0  # 隱藏時間

        self.image = self.run_img[0]
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.hitbox = pygame.Rect(self.rect.x, self.rect.y, 64, 97)

    def update(self):
        if self.hidden:
            if pygame.time.get_ticks() - self.hide_time > 1000:  # 毫秒
                self.hidden = False
                self.is_jump = False
                self.is_slide = False
                self.jump_vel = self.JUMP_VEL
                self.jump_time = 2
                self.image = self.run_img[0]
            return  # 強制中斷 update 函式，下面程式若有改動不會有影響(若用 if 就要調整 if 包含範圍)

        if self.is_jump:
            self.jump()
        elif self.is_slide:
            self.slide()
        else:
            self.walk()

        if self.step_idx >= self.ANIM_STEP * 2:
            self.step_idx = 0

        self.update_hitbox()

    def update_hitbox(self):
        if self.is_slide:
            self.hitbox = pygame.Rect(self.rect.x, self.rect.y, 86, 82)
            self.hitbox.topleft = self.rect.topleft
        else:
            self.hitbox = pygame.Rect(self.rect.x, self.rect.y, 64, 97)
            self.hitbox.midtop = self.rect.midtop

    def walk(self):
        self.is_run = True
        self.image = self.run_img[
            self.step_idx // self.ANIM_STEP
        ]  # 共2n幀，每n幀換一張圖
        self.rect = self.image.get_rect()  # 保證每張圖片都有自己的 rect 並更新位置
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_idx += 1

    def try_jump(self):
        if self.jump_time > 0:
            self.is_jump = True
            self.is_run = False
            self.is_slide = False
            self.jump_vel = self.JUMP_VEL
            self.jump_time -= 1

    def jump(self):
        self.image = self.jump_img
        self.rect.y -= self.jump_vel
        self.jump_vel -= 1

        if self.rect.y >= self.Y_POS:
            self.rect.y = self.Y_POS
            self.is_jump = False
            self.jump_vel = self.JUMP_VEL
            self.jump_time = 2

    def slide(self):
        self.is_slide = True
        self.image = self.slide_img[self.step_idx // self.ANIM_STEP]
        self.rect = self.image.get_rect()  # 保證每張圖片都有自己的 rect 並更新位置
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS_SLIDE
        self.step_idx += 1

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()  # 回傳遊戲開始後的毫秒數
        self.rect.y = self.Y_POS
        self.image = HIDE
