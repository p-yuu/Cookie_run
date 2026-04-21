import os

import pygame

# ----- 顏色設定 -----
BACKGROUND = (191, 221, 226)
YELLOW = (222, 130, 9)
LIGHT_YELLOW = (247, 228, 170)
RED = (200, 74, 51)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# ----- 基本設定 -----
FPS = 60
GAME_SPEED = 10
WIDTH = 900
HEIGHT = 500

# ----- 遊戲狀態變數 -----
# 遊戲狀態
game_speed = None
distance = None
points = None
obstacle_hidden = None
obstacle_time = None
buff_count = None

# sprite group
player_group = None
bg_group = None
obstacle_group = None
buff_group = None

# 遊戲判定
game_started = None
round_finished = None
waiting_result = None
game_result = None

# 線上模式
online_mode = False
room_full = False
my_offset = (0, 0)
opp_offset = (0, HEIGHT // 2)
scale = 1.0
scale_cache = {}
no_opponent = None
opp_die = None
opponent_player = None
opponent_obstacle = None
opponent_bg = None
my_score = None
opp_score = None
send_queue = None

# 時間
countdown_start_time = None
countdown_seconds = 3
last_send_time = None
finish_time = None

# ----- pygame 初始化 -----
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Duck Run")
CLOCK = pygame.time.Clock()


# ----- 圖片加載 -----
def load_img(path, name, size=None):
    image = pygame.image.load(os.path.join(path, name)).convert_alpha()
    if size:
        image = pygame.transform.scale(image, size)
    return image


RUNNING = [
    load_img("image", "DUCK_RUN1.PNG", (85, 110)),
    load_img("image", "DUCK_RUN2.PNG", (85, 110)),
]
JUMPING = load_img("image", "DUCK_JUMP.PNG", (85, 110))
SLIDING = [
    load_img("image", "DUCK_SLIDE1.PNG", (86, 82)),
    load_img("image", "DUCK_SLIDE2.PNG", (86, 82)),
]
HIDE = load_img("image", "DUCK_DIE.PNG", (85, 110))
LIVE = load_img("image", "DUCK_LIVES.PNG", (30, 30))
TRACK = load_img("image", "TRACK.PNG", (WIDTH, HEIGHT))
BG = load_img("image", "BG.PNG", (WIDTH, 321))
SMALL_OBT = [
    load_img("image", "OBT1-1.PNG", (76, 90)),
    load_img("image", "OBT1-2.PNG", (54, 90)),
    load_img("image", "OBT1-3.PNG", (90, 90)),
]
LARGE_OBT = [
    load_img("image", "OBT2-1.PNG", (82, 145)),
    load_img("image", "OBT2-2.PNG", (125, 145)),
    load_img("image", "OBT2-3.PNG", (73, 145)),
]
FLYING = load_img("image", "OBT_FLY.PNG", (120, 132))
BUFF = load_img("image", "BUFF.PNG", (50, 50))
DEBUFF = load_img("image", "DEBUFF.PNG", (50, 50))
MENU = load_img("image", "FINISH.PNG", (900, 500))
