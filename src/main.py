import json
import random

import config
import network
import pygame
from background import *
from buff import *
from config import (
    BACKGROUND,
    CLOCK,
    FPS,
    GAME_SPEED,
    HEIGHT,
    LIVE,
    SCREEN,
    WIDTH,
    YELLOW,
)
from draw import *
from obstacle import *
from player import *
from reset import *

show_init = True
show_finish = False
running = True

while running:
    # ------------------------ 開始 / 結束設定 -------------------------
    if show_init:
        close = draw_start_menu()
        if close:
            break

        config.scale = 0.5 if config.online_mode else 1.0
        player = reset_game(Player, Background, config.scale)

        if config.online_mode:
            success = network.init_network()
            if not success:
                network.reset_network_state()
                show_init = True
                continue

        show_init = False

    if show_finish:
        close = draw_finish_menu()
        if close:
            break
        network.reset_network_state()
        show_finish = False
        show_init = True
        config.room_full = False
        continue  # 避免遊戲邏輯執行

    if config.round_finished:
        SCREEN.fill(BACKGROUND)
        if config.online_mode:
            # 繼續繪製對手
            draw_opponent_bg(config.opponent_bg, config.scale, config.opp_offset)
            draw_opponent_obstacle(
                config.opponent_obstacle, config.scale, config.opp_offset
            )
            draw_opponent(config.opponent_player, config.scale, config.opp_offset)
            # 繪製 eliminated
            my_rect = pygame.Rect(0, 0, WIDTH, HEIGHT // 2)
            draw_eliminated_overlay(SCREEN, my_rect)
        pygame.display.update()

        if config.waiting_result and config.opp_die and not config.game_result:
            if pygame.time.get_ticks() - config.finish_time > 5000:
                print("Both die but no result")
                config.game_result = "DRAW"
                config.waiting_result = False

        if config.game_result:
            show_finish = True
        CLOCK.tick(FPS)
        continue

    # 遊戲準備及倒數
    if not config.game_started:
        if config.room_full:
            network.reset_network_state()
            show_init = True
            config.countdown_start_time = None
            continue

        if config.no_opponent:
            print("no opponent found")
            network.reset_network_state()
            show_init = True
            config.countdown_start_time = None
            continue

        if config.countdown_start_time is None:  # 是不是同一個物件
            if not config.online_mode:
                config.countdown_start_time = pygame.time.get_ticks()
            else:
                SCREEN.fill(BACKGROUND)
                draw_text(
                    SCREEN,
                    "Waiting for opponent...",
                    60,
                    WIDTH // 2,
                    HEIGHT // 2 - 60,
                    YELLOW,
                )
                pygame.display.update()
                CLOCK.tick(FPS)
                continue
        remaining = config.countdown_seconds - (
            (pygame.time.get_ticks() - config.countdown_start_time) // 1000
        )
        SCREEN.fill(BACKGROUND)
        if remaining > 0:
            draw_text(SCREEN, str(remaining), 120, WIDTH // 2, HEIGHT // 2 - 50, YELLOW)
        else:
            draw_text(SCREEN, "GO!", 120, WIDTH // 2, HEIGHT // 2 - 50, YELLOW)
            config.game_started = True

        pygame.display.update()
        CLOCK.tick(FPS)
        continue

    # CLOCK.tick(FPS) # 一秒 FPS 幀 (FPS 次迴圈) 同時回傳上一幀教過的毫秒數
    config.distance += config.game_speed * (
        CLOCK.tick(FPS) / 1000
    )  # 一幀的秒數 * 速率 = 一幀的距離
    if config.distance >= 1:
        add = int(config.distance)
        config.points += add
        config.distance -= add  # 剩餘小數點留給下一幀

    # ---------------------------- 取得輸入 ----------------------------
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

    # ---------------------------- 更新遊戲 ----------------------------
    config.bg_group.update()
    config.obstacle_group.update()
    config.buff_group.update()
    config.player_group.update()  # 執行 all_sprite 裡面每一個物件的 update() 函式

    # 障礙物生成
    if config.obstacle_hidden:
        if pygame.time.get_ticks() - config.obstacle_time > 1000:
            config.obstacle_hidden = False

    if not config.obstacle_hidden:
        if get_last_x() < WIDTH - random.randint(550, 650):
            r = random.randint(0, 5)
            if r == 0 or (config.buff_count >= 2 and r == 3):
                config.obstacle_group.add(Small_OBT())
                config.buff_count = 0
            elif r == 1 or (config.buff_count >= 2 and r == 4):
                config.obstacle_group.add(Large_OBT())
                config.buff_count = 0
            elif r == 2:
                config.obstacle_group.add(Fly_OBT())
                config.buff_count = 0
            elif r == 3:
                config.buff_group.add(Buff("speed_up"))
                config.buff_count += 1
            elif r == 4:
                config.buff_group.add(Buff("speed_down"))
                config.buff_count += 1

    # ---------------------------- 發送狀態 ----------------------------
    now = pygame.time.get_ticks()
    if config.online_mode and config.client_socket and not config.round_finished:
        if now - config.last_send_time >= 1:  # 每 1ms 傳送一次
            network.send_state(
                config.client_socket,
                player,
                config.obstacle_group,
                config.points,
                config.buff_group,
            )
            config.last_send_time = now

    # ---------------------------- 畫面顯示 ----------------------------
    SCREEN.fill(BACKGROUND)
    if config.online_mode:
        # 自己
        config.bg_group.draw(SCREEN)
        draw_group_scaled(SCREEN, config.obstacle_group, config.scale, config.my_offset)
        draw_group_scaled(SCREEN, config.buff_group, config.scale, config.my_offset)
        draw_group_scaled(SCREEN, config.player_group, config.scale, config.my_offset)
        # 對手
        draw_opponent_bg(config.opponent_bg, config.scale, config.opp_offset)
        draw_opponent_obstacle(
            config.opponent_obstacle, config.scale, config.opp_offset
        )
        draw_opponent(config.opponent_player, config.scale, config.opp_offset)
        # print(config.scale)##

    else:
        config.bg_group.draw(SCREEN)
        config.obstacle_group.draw(SCREEN)
        config.buff_group.draw(SCREEN)
        config.player_group.draw(SCREEN)

    # player v.s obstacle
    hits = [o for o in config.obstacle_group if player.hitbox.colliderect(o.rect)]
    if hits and not player.hidden:
        # pygame.draw.rect(SCREEN, (225, 0, 0), player.rect, 2) # 撞到描紅邊
        for hit in hits:
            hit.kill()
        config.game_speed = GAME_SPEED
        player.lives -= 1
        player.hide()  # 增加緩衝時間
        hide_obstacle()

    if player.lives == 0 and not config.round_finished:
        config.round_finished = True
        config.finish_time = pygame.time.get_ticks()

        if config.online_mode:
            config.waiting_result = True
            network.send_state(
                config.client_socket,
                player,
                config.obstacle_group,
                config.points,
                config.buff_group,
            )

            die_event = {"type": "EVENT", "event": "PLAYER_DIE"}
            if config.send_queue:
                config.send_queue.put((json.dumps(die_event) + "\n").encode())
            else:
                config.client_socket.sendall((json.dumps(die_event) + "\n").encode())

            data = {"type": "GAME_OVER", "score": config.points}
            if config.send_queue:
                config.send_queue.put((json.dumps(data) + "\n").encode())
            else:
                config.client_socket.sendall(json.dumps(data).encode() + b"\n")

            player.kill()
            config.obstacle_group.empty()
            config.buff_group.empty()
        else:
            config.game_result = "finish"
        continue

    # player v.s buff
    hits = [o for o in config.buff_group if player.hitbox.colliderect(o.rect)]
    for buff in hits:
        buff.kill()
        config.game_speed += buff.get_effect()
        config.game_speed = max(4, min(config.game_speed, 19))

    draw_lives(SCREEN, player.lives, LIVE, 750, 15)
    draw_text(SCREEN, f"points: {config.points}", 25, 830, 15)
    if config.online_mode:
        draw_text(SCREEN, "YOU", 30, 30, 10)
        draw_text(SCREEN, "OPPONENT", 30, 60, config.opp_offset[1] + 10)
        if config.opp_die:
            opp_rect = pygame.Rect(0, config.opp_offset[1], WIDTH, config.opp_offset[1])
            draw_eliminated_overlay(SCREEN, opp_rect)
    pygame.display.update()

pygame.quit()
