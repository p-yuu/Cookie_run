import json
import socket
import threading
from queue import Empty, Queue

import pygame

import config
from config import SCREEN
from draw import *

SERVER_IP = "192.168.0.111"
SERVER_PORT = 5050


def input_room():
    room = ""
    active = True

    while active:
        SCREEN.fill((220, 220, 220))
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
                    room += e.unicode  # 實際輸入的字元


def init_network():
    try:
        config.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        config.client_socket.connect((SERVER_IP, SERVER_PORT))
        room = input_room()
        if not room:
            config.online_mode = False
            return False

        # use send queue to avoid blocking main thread
        config.send_queue = Queue()
        config.send_queue.put(f"ROOM {room}\n".encode())

        # start listener, pinger, and sender threads
        threading.Thread(
            target=listen_server, args=(config.client_socket,), daemon=True
        ).start()
        threading.Thread(
            target=ping_server, args=(config.client_socket,), daemon=True
        ).start()
        threading.Thread(
            target=send_worker, args=(config.client_socket,), daemon=True
        ).start()

        config.online_mode = True
        print("online mode")
        return True
    except Exception as e:
        config.online_mode = False
        print("offline mode", e)
        return False


def reset_network_state():
    config.game_started = False
    try:
        if config.client_socket:
            config.client_socket.close()
    except:
        pass
    config.client_socket = None
    config.online_mode = False
    if config.send_queue:
        try:
            while True:
                config.send_queue.get_nowait()
        except Empty:
            pass
        config.send_queue = None


def listen_server(sock):
    buffer = ""

    while config.online_mode:
        try:
            data = sock.recv(8192)
            if not data:
                break

            buffer += data.decode()
            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)

                if msg == "START":
                    config.countdown_start_time = pygame.time.get_ticks()
                    continue
                if msg == "NO_OPPONENT":
                    config.no_opponent = True
                    continue
                if msg == "ROOM_FULL":
                    config.room_full = True
                    print("Room is full")
                    continue
                else:
                    payload = json.loads(msg)
                    if payload["type"] == "GAME_RESULT":
                        config.waiting_result = False
                        config.game_result = payload["RESULT"]
                        config.my_score = payload["MY_SCORE"]
                        config.opp_score = payload["OPP_SCORE"]
                    elif payload["type"] == "OPPONENT_LEFT":
                        config.opp_die = True
                        if not config.round_finished:
                            config.game_result = "WIN"
                            config.waiting_result = False
                    elif payload["type"] == "EVENT":
                        config.opp_die = True
                    elif payload["type"] == "STATE":
                        config.opponent_player = payload.get("player")
                        config.opponent_obstacle = payload.get("obstacles")
                        config.opponent_bg = payload.get("background")

        except json.JSONDecodeError:  # 半包 / 黏包，正常，忽略
            continue

        except OSError:  # 真正斷線
            config.online_mode = False
            break

        except Exception as e:
            print("[listen_server error]", e)
            continue


def ping_server(sock):  # 連線判斷 (心跳)
    while config.online_mode:
        try:
            ping = {"type": "PING"}
            if config.send_queue:
                config.send_queue.put((json.dumps(ping) + "\n").encode())
            else:
                sock.sendall((json.dumps(ping) + "\n").encode())
        except Exception as e:
            print("[PING ERROR]", e)
            break
        pygame.time.wait(5000)  # 每 5 秒送一次


def send_state(sock, player, obstacles, points, buff):
    player_state = {
        "type": "PLAYER_STATE",
        "x": player.rect.x,
        "y": player.rect.y,
        "is_jump": player.is_jump,
        "is_slide": player.is_slide,
        "hidden": player.hidden,
        "points": points,
        "lives": player.lives,
    }

    obstacles_state = {
        "obstacles": [
            {"x": o.rect.x, "y": o.rect.y, "kind": o.kind, "index": o.index}
            for o in obstacles
        ],
        "buffs": [
            {"x": b.rect.x, "y": b.rect.y, "effect": b.get_effect()} for b in buff
        ],
    }

    track_x = min(b.rect.x for b in config.bg_group if b.mode == "track")
    bg_x = min(b.rect.x for b in config.bg_group if b.mode == "bg")

    background_state = {"track_x": track_x, "bg_x": bg_x}

    data = {
        "type": "STATE",
        "time": pygame.time.get_ticks(),
        "player": player_state,
        "obstacles": obstacles_state,
        "background": background_state,
    }

    if config.send_queue:
        config.send_queue.put((json.dumps(data) + "\n").encode())
    else:
        sock.sendall((json.dumps(data) + "\n").encode())


def send_worker(sock):
    while config.online_mode and sock:
        try:
            data = config.send_queue.get(timeout=0.5)  # 最多等 0.5 秒
        except Exception:
            continue
        try:
            # t1 = pygame.time.get_ticks()
            sock.sendall(data)
            # t2 = pygame.time.get_ticks()
            # print(f"[send_worker] sent {len(data)} bytes at {t1}ms (dur {t2 - t1}ms)")
        except Exception as e:
            print("[send_worker error]", e)
            break
