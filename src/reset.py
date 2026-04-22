import pygame

import config
from config import BG, TRACK, WIDTH


def reset_game(PlayerClass, BackgroundClass, scale=1.0):
    # ------- 重建玩家和背景 -------
    config.player_group = pygame.sprite.Group()
    player = PlayerClass()
    config.player_group.add(player)

    config.bg_group = pygame.sprite.Group()
    for i in range(4):
        config.bg_group.add(BackgroundClass(BG, "bg", i * WIDTH, scale))
        config.bg_group.add(BackgroundClass(TRACK, "track", i * WIDTH, scale))

    config.obstacle_group = pygame.sprite.Group()
    config.buff_group = pygame.sprite.Group()

    # ---------- 變數重置 ----------
    # 基本設定
    config.game_speed = config.GAME_SPEED
    config.distance = 0
    config.points = 0
    config.obstacle_hidden = False
    config.obstacle_time = 0
    config.buff_count = 0

    # 雙人 PK 設定
    config.room_full = False  # 房間已有兩個人
    config.round_finished = False  # 本地端結束
    config.waiting_result = False  # 等待server的遊戲結果
    config.game_result = None  # WIN / LOSE / DRAW
    config.game_started = False
    config.no_opponent = False  # 沒有配對到對手
    config.opp_die = False  # 對手死亡
    config.my_score = None
    config.opp_score = None

    # 創建影子角色
    config.opponent_player = None
    config.opponent_obstacle = None
    config.opponent_bg = None

    # 計時
    config.last_send_time = 0  # 傳送資料
    config.countdown_start_time = None
    config.finish_time = None  # 本地端結束遊戲時間

    return player
