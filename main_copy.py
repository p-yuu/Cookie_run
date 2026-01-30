import pygame
import os
import random

FPS = 60
BACKGROUND = (191,221,226)
YELLOW = (222,130,9)
RED = (200,74,51)
BLACK = (0,0,0)

WIDTH = 900
HEIGHT = 500

#遊戲初始化
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Cookie Run")
CLOCK = pygame.time.Clock()

#image
RUNNING = [pygame.transform.scale(pygame.image.load(os.path.join("image", "DOCK_RUN1.PNG")).convert_alpha(), (85,110)),
           pygame.transform.scale(pygame.image.load(os.path.join("image", "DOCK_RUN2.PNG")).convert_alpha(), (85,110))]
JUMPING = pygame.transform.scale(pygame.image.load(os.path.join("image", "DOCK_JUMP.PNG")).convert_alpha(), (85,110))
SLIDING = [pygame.transform.scale(pygame.image.load(os.path.join("image", "DOCK_SLIDE1.PNG")).convert_alpha(), (86,82)),
           pygame.transform.scale(pygame.image.load(os.path.join("image", "DOCK_SLIDE2.PNG")).convert_alpha(), (86,82))]
HIDE = pygame.transform.scale(pygame.image.load(os.path.join("image", "DOCK_DIE.PNG")).convert_alpha(), (85,110))
LIVE = pygame.transform.scale(pygame.image.load(os.path.join("image", "DOCK_LIVES.PNG")).convert_alpha(), (30,30))
CLOUD = pygame.transform.scale(pygame.image.load(os.path.join("image", "CLOUD.PNG")).convert_alpha(), (100,75))
TRACK = pygame.transform.scale(pygame.image.load(os.path.join("image", "TRACK.PNG")).convert_alpha(), (WIDTH,HEIGHT))
BG = pygame.transform.scale(pygame.image.load(os.path.join("image", "BG.PNG")).convert_alpha(), (WIDTH,321))
SMALL_OBT = [pygame.transform.scale(pygame.image.load(os.path.join("image", "OBT1-1.PNG")).convert_alpha(), (76,90)),
           pygame.transform.scale(pygame.image.load(os.path.join("image", "OBT1-2.PNG")).convert_alpha(), (54,90)),
           pygame.transform.scale(pygame.image.load(os.path.join("image", "OBT1-3.PNG")).convert_alpha(), (90,90))]
LARGE_OBT = [pygame.transform.scale(pygame.image.load(os.path.join("image", "OBT2-1.PNG")).convert_alpha(), (82,145)),
           pygame.transform.scale(pygame.image.load(os.path.join("image", "OBT2-2.PNG")).convert_alpha(), (125,145)),
           pygame.transform.scale(pygame.image.load(os.path.join("image", "OBT2-3.PNG")).convert_alpha(), (73,145))]
FLYING = pygame.transform.scale(pygame.image.load(os.path.join("image", "OBT_FLY.PNG")).convert_alpha(), (100,50))
BUFF = pygame.transform.scale(pygame.image.load(os.path.join("image", "BUFF.PNG")).convert_alpha(), (50,50))
DEBUFF = pygame.transform.scale(pygame.image.load(os.path.join("image", "DEBUFF.PNG")).convert_alpha(), (50,50))
MENU = pygame.transform.scale(pygame.image.load(os.path.join("image", "FINISH.PNG")).convert_alpha(), (900,500))

#text
def draw_text(surf, text, size, x, y, color = BLACK):
    font = pygame.font.Font('Caroni-Regular.otf', size)
    text_surface = font.render(text, True, color) #True: 文字反鋸齒
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

#player
class Player(pygame.sprite.Sprite):
    X_POS = 80
    Y_POS = 310
    Y_POS_SLIDE = 338
    JUMP_VEL = 16

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.slide_img = SLIDING

        self.is_run = True
        self.is_jump = False
        self.is_slide = False

        self.step_idx = 0    #步驟索引
        self.anim_step = 10  #多少幀一張圖

        self.jump_vel = self.JUMP_VEL
        self.jump_time = 2
        self.on_ground = True

        self.lives = 3
        self.hidden = False
        self.hide_time = 0 #隱藏時間

        self.image = self.run_img[0]
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS

    def update(self):
        if self.hidden:
            if pygame.time.get_ticks() - self.hide_time > 1000: #毫秒
                self.hidden = False
                self.is_jump = False
                self.is_slide = False
                self.jump_vel = self.JUMP_VEL
                self.jump_time = 2
                self.image = self.run_img[0]
            return # 強制中斷 update 函式，下面程式若有改動不會有影響(若用 if 就要調整 if 包含範圍)

        if self.is_jump:
            self.jump()
        elif self.is_slide:
            self.slide()
        else:
            self.walk()
        
        if self.step_idx >= self.anim_step * 2:
            self.step_idx = 0

    def walk(self):
        self.is_run = True
        self.image = self.run_img[self.step_idx // self.anim_step] #共2n幀，每n幀換一張圖
        self.rect = self.image.get_rect() #保證每張圖片都有自己的 rect 並更新位置
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
        self.image = self.slide_img[self.step_idx // self.anim_step]
        self.rect = self.image.get_rect() #保證每張圖片都有自己的 rect 並更新位置
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS_SLIDE
        self.step_idx += 1
    
    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks() # 回傳遊戲開始後的毫秒數
        self.rect.y = self.Y_POS
        self.image = HIDE

def draw_lives(SCREEN, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x - i * 35
        img_rect.y = y
        SCREEN.blit(img, img_rect)

#obstacle
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, images, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = images
        self.index = 0
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = y

    def update(self):
        self.rect.x -= game_speed
        if self.rect.right <= 0:
            self.kill()

def Small_OBT():
    img = random.choice(SMALL_OBT)
    return Obstacle(img, 320) # 回傳圖片為 list

def Large_OBT():
    img = random.choice(LARGE_OBT)
    return Obstacle(img, 265)

def Fly_OBT():
    return Obstacle(FLYING, 270)

def hide_obstacle(): # 隱藏障礙物
    global obstacle_hidden, obstacle_time # 取得全域變數並修改他，而非創建新的變數
    obstacle_hidden = True
    obstacle_time = pygame.time.get_ticks()
    obstacle_group.empty() # 清空畫面上的障礙物
    buff_group.empty()

def get_last_x(): #取得最右物件
    xs = []
    for s in obstacle_group:
        xs.append(s.rect.right)
    for s in buff_group:
        xs.append(s.rect.right)
    return max(xs) if xs else 0

#buff
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
        self.rect.y = random.choice([240,355])
    
    def update(self):
        self.rect.x -= game_speed
        if self.rect.right <= 0:
            self.kill()
    
    def get_effect(self):
        return self.effect

#background
class Background(pygame.sprite.Sprite):
    def __init__(self, img, mode, x_offset = 0):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x_offset
        self.rect.y = 0
        self.mode = mode
    
    def update(self):
        if self.mode == 'track':
            self.rect.x -= game_speed
        else:
            self.rect.x -= game_speed - 3
        if self.rect.right <= 0:
            self.rect.x = round(self.rect.width * 3 - abs(self.rect.right))

def draw_menu(mode):
    SCREEN.blit(MENU, (0,0))
    if mode == 'init':
        draw_text(SCREEN, 'DOCK DOCK DOCK !!', 60, 670, 170, YELLOW)
        draw_text(SCREEN, 'press any key to', 50, 650, 240, YELLOW)
        draw_text(SCREEN, 'start the game', 50, 650, 290, YELLOW)
    else:
        draw_text(SCREEN, 'GAME OVER', 70, 650, 170, RED)
        draw_text(SCREEN, f'Final Score: {points}', 60, 660, 240, RED)
        draw_text(SCREEN, 'press any key to restart the game', 35, 670, 320, RED)
    pygame.display.update()
    waiting = True
    while waiting:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False    

def reset():
    global player_group, bg_group, obstacle_group, buff_group
    global game_speed, distance, points, obstacle_hidden, obstacle_time, buff_count
    #Group
    player_group = pygame.sprite.Group()
    player = Player()
    player_group.add(player)

    bg_group = pygame.sprite.Group()
    for i in range(4):
        bg_group.add(Background(BG, 'bg', i * WIDTH))
        bg_group.add(Background(TRACK, 'track', i * WIDTH))

    obstacle_group = pygame.sprite.Group()
    buff_group = pygame.sprite.Group()

    #global variables
    game_speed = 10 # 4 ~ 19
    distance = 0
    points = 0
    obstacle_hidden = False
    obstacle_time = 0
    buff_count = 0
    return player
    
#遊戲迴圈
show_init = True
show_finish = False
first_start = True
running = True

while running:
    #------------------------ 開始 / 結束設定 -------------------------
    if show_init:
        if first_start:
            close = draw_menu('init')
            if close:
                break
        show_init = False
        first_start = False
        player = reset()
        
    if show_finish:
        close = draw_menu('finish')
        if close: 
            break
        show_finish = False
        show_init = True
        continue # 避免遊戲邏輯執行

    # CLOCK.tick(FPS) # 一秒 FPS 幀 (FPS 次迴圈) 同時回傳上一幀教過的毫秒數
    distance += game_speed * (CLOCK.tick(FPS) / 1000) # 一幀的秒數 * 速率 = 一幀的距離
    if distance >= 1:
        add = int(distance)
        points += add
        distance -= add # 剩餘小數點留給下一幀

    #---------------------------- 取得輸入 ----------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_SPACE):
                player.try_jump()
            elif event.key == pygame.K_DOWN:
                player.is_slide = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player.is_slide = False

    #---------------------------- 更新遊戲 ----------------------------
    bg_group.update()
    obstacle_group.update()
    buff_group.update()
    player_group.update() #執行 all_sprite 裡面每一個物件的 update() 函式

    # 障礙物生成
    if obstacle_hidden:
        if pygame.time.get_ticks() - obstacle_time > 1000:  
            obstacle_hidden = False

    if not obstacle_hidden:
        if get_last_x() < WIDTH - random.randint(550,650):
            r = random.randint(0,5)
            if r == 0 or (buff_count >= 2 and r == 3):
                obstacle_group.add(Small_OBT())
                buff_count = 0
            elif r == 1 or (buff_count >= 2 and r == 4):
                obstacle_group.add(Large_OBT())
                buff_count = 0
            elif r == 2:
                obstacle_group.add(Fly_OBT())
            elif r == 3:
                buff = Buff("speed_up")
                buff_group.add(buff)
                buff_count += 1
            elif r == 4:
                buff = Buff("speed_down")
                buff_group.add(buff)
                buff_count += 1

    #---------------------------- 畫面顯示 ----------------------------
    SCREEN.fill(BACKGROUND) # 要先填滿背景色，不然上次畫的會無法被覆蓋
    bg_group.draw(SCREEN)
    obstacle_group.draw(SCREEN)
    buff_group.draw(SCREEN)
    player_group.draw(SCREEN)

    # player v.s obstacle
    hits = pygame.sprite.spritecollide(player, obstacle_group, False)
    if hits and not player.hidden:
        # pygame.draw.rect(SCREEN, (225, 0, 0), player.rect, 2) # 撞到描紅邊
        player.lives -= 1
        player.hide() #增加緩衝時間
        hide_obstacle()

    # if player.hidden:
    #     SCREEN.blit(HIDE, (player.X_POS, player.Y_POS))

    if player.lives == 0:
        show_finish = True
        
    # player v.s buff
    hits = pygame.sprite.spritecollide(player, buff_group, True)
    for buff in hits:
        game_speed += buff.get_effect()
        game_speed = max(4, min(game_speed, 19))
    
    draw_lives(SCREEN, player.lives, LIVE, 750, 15)
    draw_text(SCREEN, f"points: {points}", 25, 830, 15)
    pygame.display.update()

pygame.quit()