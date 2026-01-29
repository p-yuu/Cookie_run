import pygame
import os
import random

#------------------------------ network init ------------------------------
import json
import socket
import threading

SERVER_IP = "127.0.0.1" # 要改
SERVER_PORT = 5000
#---------------------------------------------------------------------------

# 變數
FPS = 60
BACKGROUND = (191,221,226)
YELLOW = (222,130,9)
LIGHT_YELLOW = (247,228,170)
RED = (200,74,51)
BLACK = (0,0,0)
WHITE = (255,255,255)

WIDTH = 900
HEIGHT = 500

# pygame 初始化
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Cookie Run")
CLOCK = pygame.time.Clock()

# image
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
                self.rect.y = self.Y_POS
                self.rect.x = self.X_POS
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
    def __init__(self, images, y, kind, idx):
        pygame.sprite.Sprite.__init__(self)

        self.image = images
        self.index = 0
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = y
        self.index = idx # for json
        self.kind = kind # for json

    def update(self):
        self.rect.x -= game_speed
        if self.rect.right <= 0:
            self.kill()

def Small_OBT():
    idx = random.randint(0,2)
    return Obstacle(SMALL_OBT[idx], 320, "small", idx)

def Large_OBT():
    idx = random.randint(0,2)
    return Obstacle(LARGE_OBT[idx], 265, "large", idx)

def Fly_OBT():
    return Obstacle(FLYING, 270, "fly", 0)

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
    def __init__(self, img, mode, x_offset = 0, scale = 1.0):
        pygame.sprite.Sprite.__init__(self)
        self.image = img.copy() # 使用副本避免尺寸更改影響到未來
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale), int(self.image.get_height() * scale)))
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
            self.rect.x = round(self.rect.width * 3 + self.rect.right)

def reset_game():
    global player_group, bg_group, obstacle_group, buff_group
    global game_speed, distance, points, obstacle_hidden, obstacle_time, buff_count
    global opponent_player, game_started, round_finished, waiting_result, game_result
    global no_opponent, opp_die, opponent_obstacle, opponent_points, my_score, opp_score
    global last_send_time, countdown_start_time, finish_time
    
    # ------- 重建玩家和背景 -------
    player_group = pygame.sprite.Group()
    player = Player()
    player_group.add(player)

    bg_group = pygame.sprite.Group()
    for i in range(4):
        bg_group.add(Background(BG, 'bg', i * WIDTH * scale, scale))
        bg_group.add(Background(TRACK, 'track', i * WIDTH * scale, scale))

    obstacle_group = pygame.sprite.Group()
    buff_group = pygame.sprite.Group()

    # ---------- 變數重置 ----------
    # 基本設定
    game_speed = 10
    distance = 0
    points = 0
    obstacle_hidden = False
    obstacle_time = 0
    buff_count = 0

    # 雙人 PK 設定
    round_finished = False    # 本地端結束
    waiting_result = False    # 等待server的遊戲結果
    game_result = None        # WIN / LOSE / DRAW
    game_started = False
    no_opponent = False       # 沒有配對到對手
    opp_die = False           # 對手死亡
    my_score = None
    opp_score = None

    # 創建影子角色
    opponent_player = None
    opponent_obstacle = None
    opponent_points = 0

    # 計時
    last_send_time = 0          # 傳送資料
    countdown_start_time = None # 倒數計時
    finish_time = None          # 本地端結束遊戲時間

    return player

def draw_start_menu():
    global online_mode

    SCREEN.blit(MENU, (0,0))
    draw_text(SCREEN, 'DOCK DOCK DOCK !!', 60, 670, 170, YELLOW)

    single_rect = pygame.Rect(550, 265, 200, 50)
    multi_rect = pygame.Rect(550, 330, 200, 50)
    pygame.draw.rect(SCREEN, LIGHT_YELLOW, single_rect)
    pygame.draw.rect(SCREEN, LIGHT_YELLOW, multi_rect)
    draw_text(SCREEN, 'Single Plyer', 50, 650, 260, YELLOW)
    draw_text(SCREEN, 'Battle', 50, 650, 330, YELLOW)

    pygame.display.update()
    waiting = True
    while waiting:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if single_rect.collidepoint(event.pos):
                    online_mode = False
                    print("offline mode")
                elif multi_rect.collidepoint(event.pos):
                    online_mode = True
                    print("online mode")
                return False
            
def draw_finish_menu():
    SCREEN.blit(MENU, (0,0))
    if online_mode:
        draw_text(SCREEN, f'YOU {game_result}', 70, 650, 170, RED)
        draw_text(SCREEN, f'{my_score} V.S {opp_score}', 50, 650, 250, RED)
        draw_text(SCREEN, 'press any key to restart the game', 35, 670, 320, RED)
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

def draw_eliminated_overlay(SCREEN, rect):
    overlay = pygame.Surface((rect.width, rect.height))
    overlay.fill((108,125,128))
    SCREEN.blit(overlay, rect.topleft)

    draw_text(SCREEN, "ELIMINATED", 60, rect.centerx, rect.centery, RED)

#------------------------------ network ---------------------------------------
def input_room():
    room = ""
    active = True

    while active:
        SCREEN.fill((220,220,220))
        draw_text(SCREEN, f"Enter Room ID: {room}", 40, 450, 200)
        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return room
                elif e.key == pygame.K_BACKSPACE:
                    room = room[:-1]  # 刪掉最後一個字元
                else:
                    room += e.unicode # 實際輸入的字元

def init_network():
    global client_socket, online_mode
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        room = input_room()
        if not room:
            online_mode = False
            return False
        client_socket.sendall(f"ROOM {room}\n".encode())
        
        threading.Thread(            # 開一個背景分身 (可同時執行遊戲跟接收)
            target=listen_server,    # 執行哪個函式
            args=(client_socket,),   # 傳遞參數 (tuple)
            daemon=True              # 定義此thread為背景執行緒 (主程式結束自動結束)
        ).start()                    # 啟動 thread

        online_mode = True
        print("online mode")
        return True
    except:
        online_mode = False
        print("offline mode")
        return False

def reset_network_state():
    global game_started, online_mode, client_socket, opponent_state
    game_started = False
    try:
        client_socket.close()
    except:
        pass

def listen_server(sock):
    global opponent_player, opponent_obstacle, online_mode, countdown_start_time
    global game_started, no_opponent, opp_die, game_result, waiting_result, my_score, opp_score
    buffer = ""

    while online_mode == True:
        try:
            data = sock.recv(8192)
            if not data:
                break

            buffer += data.decode()
            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)

                if msg == "START":
                    countdown_start_time = pygame.time.get_ticks()
                if msg == "NO_OPPONENT":
                    no_opponent = True
                else:
                    payload = json.loads(msg)
                    if payload["type"] == "GAME_RESULT":
                        waiting_result = False
                        game_result = payload["RESULT"]
                        my_score = payload["MY_SCORE"]
                        opp_score = payload["OPP_SCORE"]
                    elif payload["type"] == "PLAYER_STATE":
                        opponent_player = payload
                        if opponent_player["lives"] == 0:
                            opp_die = True
                    elif payload['type'] == "OBSTACLES_STATE":
                        opponent_obstacle = payload

        except json.JSONDecodeError:   # 半包 / 黏包，正常，忽略
            continue

        except OSError:   # 真正斷線
            online_mode = False
            break

        except Exception as e:
            print("[listen_server error]", e)
            continue

def send_player_state(sock, player, points):
    data = {
        "type": "PLAYER_STATE",
        "x": player.rect.x,
        "y": player.rect.y,
        "is_jump": player.is_jump,
        "is_slide": player.is_slide,
        "hidden": player.hidden,
        "points": points,
        "lives": player.lives,
    }
    message = json.dumps(data).encode() + b'\n' # dict 轉換成 JSON 再轉成 bytes
    sock.sendall(message)

def send_obstacles_state(sock, obstacles, buff):
    data = {
        "type": "OBSTACLES_STATE",
        "obstacles": [{"x": o.rect.x, "y": o.rect.y, "kind": o.kind, "index": o.index} for o in obstacles],
        "buffs": [{"x": b.rect.x, "y": b.rect.y, "effect": b.get_effect()} for b in buff]
    }
    message = json.dumps(data).encode() + b'\n'
    sock.sendall(message)

def get_scaled(img, scale): # 縮放圖片
    key = (img, scale)
    if key not in scale_cache:
        w, h = img.get_size()
        scale_cache[key] = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
    return scale_cache[key]

def draw_group_scaled(SCREEN, group, scale = 1.0, offset = (0,0)): # 繪製縮放過的圖片
    for sprite in group:
        img = get_scaled(sprite.image, scale)
        x = int(sprite.rect.x + offset[0])
        y = int(sprite.rect.y * scale + offset[1])
        SCREEN.blit(img, (x,y))

# 繪製影子對手
def draw_opponent(state, scale, offset):
    global opponent_points

    if not state:
        return
    
    if state.get("is_jump"):
        img = JUMPING
    elif state.get("is_slide"):
        img = SLIDING[0]
    elif state.get("hidden"):
        img = HIDE
    else:
        img = RUNNING[0]
    img = get_scaled(img, scale)
    x = int(state["x"] + offset[0])
    y = int(state["y"] * scale + offset[1])
    opponent_points = state["points"]

    img = img.copy()
    img.set_alpha(150) # 透明度: 0 ~ 255
    SCREEN.blit(img, (x, y))

def draw_opponent_obstacle(state, scale, offset):
    if not state:
        return

    for o in state["obstacles"]:
        if o["kind"] == "small":
            img = SMALL_OBT[o["index"]]
        elif o["kind"] == "large":
            img = LARGE_OBT[o["index"]]
        else:
            img = FLYING

        img = get_scaled(img, scale)
        x = int(o["x"] + offset[0])
        y = int(o["y"] * scale + offset[1])

        img = img.copy()
        img.set_alpha(150)
        SCREEN.blit(img, (x, y))

    for b in state["buffs"]:
        img = BUFF if b["effect"] > 0 else DEBUFF
        img = get_scaled(img, scale)
        x = int(b["x"] + offset[0])
        y = int(b["y"] * scale + offset[1])

        img = img.copy()
        img.set_alpha(150)
        SCREEN.blit(img, (x, y))

#--------------------------------------------------------------------------

#遊戲迴圈
show_init = True
show_finish = False
running = True

online_mode = False

my_offset = (0,0)
opp_offset = (0,HEIGHT // 2)
scale = 1.0
scale_cache = {}

countdown_seconds = 3

while running:
    #------------------------ 開始 / 結束設定 -------------------------
    if show_init:
        close = draw_start_menu()
        if close:
            break

        if online_mode:
            success = init_network()
            if not success:
                reset_network_state()
                show_init = True
                continue

        scale = 0.5 if online_mode else 1.0
        player = reset_game()
        show_init = False
    
    if show_finish:
        close = draw_finish_menu()
        if close: 
            break
        reset_network_state()
        show_finish = False
        show_init = True
        continue # 避免遊戲邏輯執行

    if round_finished:
        my_rect = pygame.Rect(0, 0, WIDTH, HEIGHT // 2)
        draw_eliminated_overlay(SCREEN, my_rect)
        pygame.display.update()

        if waiting_result and opp_die and not game_result:
            if pygame.time.get_ticks() - finish_time > 5000:
                print("Both die but no result")
                game_result = "DRAW"
                waiting_result = False

        if game_result:
            show_finish = True
        CLOCK.tick(30)
        continue

    # 遊戲準備及倒數
    if not game_started:
        if no_opponent:
            print("no opponent found") ##
            reset_network_state()
            show_init = True
            countdown_start_time = None
            continue

        if countdown_start_time is None: # 是不是同一個物件
            if not online_mode:
                countdown_start_time = pygame.time.get_ticks()
            else:
                SCREEN.fill(BACKGROUND)
                draw_text(SCREEN, "Waiting for opponent...", 60, WIDTH // 2, HEIGHT // 2 - 60, YELLOW)
                pygame.display.update()
                CLOCK.tick(30)
                continue
        remaining = countdown_seconds - ((pygame.time.get_ticks() - countdown_start_time) // 1000)
        SCREEN.fill(BACKGROUND)
        if remaining > 0:
            draw_text(SCREEN, str(remaining), 120, WIDTH // 2, HEIGHT // 2 - 50, YELLOW)
        else:
            draw_text(SCREEN, "GO!", 120, WIDTH // 2, HEIGHT // 2 - 50, YELLOW)
            game_started = True
            countdown_start_time = None
        
        pygame.display.update()
        CLOCK.tick(30)
        continue

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

    #---------------------------- 發送狀態 ----------------------------
    now = pygame.time.get_ticks()
    if online_mode and client_socket and not round_finished:
        if now - last_send_time >= 50: # 每 100ms 傳送一次
            send_player_state(client_socket, player, points)
            send_obstacles_state(client_socket, obstacle_group, buff_group)
            last_send_time = now

    #---------------------------- 畫面顯示 ----------------------------
    SCREEN.fill(BACKGROUND)
    if online_mode:
        # 自己
        # draw_group_scaled(SCREEN, bg_group, scale, my_offset)
        bg_group.draw(SCREEN)
        draw_group_scaled(SCREEN, obstacle_group, scale, my_offset)
        draw_group_scaled(SCREEN, buff_group, scale, my_offset)
        draw_group_scaled(SCREEN, player_group, scale, my_offset)
        # 對手
        draw_opponent_obstacle(opponent_obstacle, scale, opp_offset)
        draw_opponent(opponent_player, scale, opp_offset)

    else:
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

    if player.lives == 0 and not round_finished:
        round_finished = True
        finish_time = pygame.time.get_ticks()

        if online_mode:
            waiting_result = True
            send_player_state(client_socket, player, points)

            data = {
                "type": "GAME_OVER",
                "score": points
            }
            client_socket.sendall(json.dumps(data).encode() + b"\n")

            player.kill()
            obstacle_group.empty()
            buff_group.empty()
        else:
            game_result = "finish"
        continue
        
    # player v.s buff
    hits = pygame.sprite.spritecollide(player, buff_group, True)
    for buff in hits:
        game_speed += buff.get_effect()
        game_speed = max(4, min(game_speed, 19))
    
    draw_lives(SCREEN, player.lives, LIVE, 750, 15)
    draw_text(SCREEN, f"points: {points}", 25, 830, 15)
    if online_mode and opp_die:
        opp_rect = pygame.Rect(0, HEIGHT // 2, WIDTH, HEIGHT // 2)
        draw_eliminated_overlay(SCREEN, opp_rect)
    pygame.display.update()

pygame.quit()