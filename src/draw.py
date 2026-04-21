import config
import pygame
from config import (
    BG,
    BLACK,
    BUFF,
    CLOCK,
    DEBUFF,
    FLYING,
    FPS,
    HEIGHT,
    HIDE,
    JUMPING,
    LARGE_OBT,
    LIGHT_YELLOW,
    LIVE,
    MENU,
    RED,
    RUNNING,
    SCREEN,
    SLIDING,
    SMALL_OBT,
    TRACK,
    YELLOW,
)


# 基礎遊戲
def draw_lives(SCREEN, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x - i * 35
        img_rect.y = y
        SCREEN.blit(img, img_rect)


def draw_text(surf, text, size, x, y, color=BLACK):
    font = pygame.font.Font("text/Caroni-Regular.otf", size)
    text_surface = font.render(text, True, color)  # True: 文字反鋸齒
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)


def draw_start_menu():
    SCREEN.blit(MENU, (0, 0))
    draw_text(SCREEN, "DUCK DUCK DUCK !!", 60, 670, 170, YELLOW)

    single_rect = pygame.Rect(550, 265, 200, 50)
    multi_rect = pygame.Rect(550, 330, 200, 50)
    pygame.draw.rect(SCREEN, LIGHT_YELLOW, single_rect)
    pygame.draw.rect(SCREEN, LIGHT_YELLOW, multi_rect)
    draw_text(SCREEN, "Single Player", 50, 650, 260, YELLOW)
    draw_text(SCREEN, "Battle", 50, 650, 330, YELLOW)
    if config.room_full:
        draw_text(SCREEN, "The room is full", 35, 650, 385, RED)

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
                    config.online_mode = False
                    print("offline mode")
                elif multi_rect.collidepoint(event.pos):
                    config.online_mode = True
                    print("online mode")
                return False


def draw_finish_menu():
    SCREEN.blit(MENU, (0, 0))
    if config.online_mode:
        draw_text(SCREEN, f"YOU {config.game_result}", 70, 650, 170, RED)
        draw_text(
            SCREEN, f"{config.my_score} V.S {config.opp_score}", 50, 650, 250, RED
        )
        draw_text(SCREEN, "press ENTER to restart the game", 35, 670, 320, RED)
    else:
        draw_text(SCREEN, "GAME OVER", 70, 650, 170, RED)
        draw_text(SCREEN, f"Final Score: {config.points}", 60, 660, 240, RED)
        draw_text(SCREEN, "press ENTER to restart the game", 35, 670, 320, RED)
    pygame.display.update()
    waiting = True
    while waiting:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    return False


# 連線遊戲
def get_scaled(img, scale):  # 縮放圖片
    key = (img, scale)
    if key not in config.scale_cache:
        w, h = img.get_size()
        config.scale_cache[key] = pygame.transform.scale(
            img, (int(w * scale), int(h * scale))
        )
    return config.scale_cache[key]


def draw_group_scaled(SCREEN, group, scale=1.0, offset=(0, 0)):  # 繪製縮放過的圖片
    for sprite in group:
        img = get_scaled(sprite.image, scale)
        x = int(sprite.rect.x + offset[0])
        y = int(sprite.rect.y * scale + offset[1])
        SCREEN.blit(img, (x, y))


def draw_opponent(state, scale, offset):
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

    draw_lives(SCREEN, state["lives"], LIVE, 750, HEIGHT // 2 + 15)
    draw_text(SCREEN, f"points: {state['points']}", 25, 830, HEIGHT // 2 + 15)

    img = img.copy()
    img.set_alpha(150)  # 透明度: 0 ~ 255
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


def draw_opponent_bg(state, scale, offset):
    if not state:
        return

    track_base = int(state["track_x"])
    bg_base = int(state["bg_x"])

    track_img = get_scaled(TRACK, scale)
    bg_img = get_scaled(BG, scale)

    for i in range(4):
        SCREEN.blit(
            track_img, (track_base + i * track_img.get_width() + offset[0], offset[1])
        )
        SCREEN.blit(bg_img, (bg_base + i * bg_img.get_width() + offset[0], offset[1]))


def draw_eliminated_overlay(SCREEN, rect):
    overlay = pygame.Surface((rect.width, rect.height))
    overlay.fill((108, 125, 128))
    SCREEN.blit(overlay, rect.topleft)

    draw_text(SCREEN, "ELIMINATED", 60, rect.centerx, rect.centery, RED)
