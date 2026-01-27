import socket
import json

def recv_lines(sock):
    buffer = ""
    while True:
        data = sock.recv(1024).decode()
        if not data:
            break
        buffer += data
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            yield line

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 5000)) # 192.168.0.104

# 加入房間
sock.sendall(f"ROOM 123\n".encode())

# 等待 START
for line in recv_lines(sock):
    if line == "START":
        print("Game START!")
        break

# 模擬遊戲狀態傳送
import time, random
for i in range(10):
    state = {
        "type": "STATE",
        "player": {"x": 80, "y": random.randint(200, 310),
                   "is_jump": random.choice([True, False]),
                   "is_slide": random.choice([True, False]),
                   "lives": random.randint(1,3)},
        "game": {"speed": random.randint(8,15), "points": i*100},
        "obstacles": [{"x": random.randint(400,900), "y":320, "kind":"small"}],
        "buffs": [{"x": random.randint(500,900), "y":240, "kind":"speed_up"}]
    }
    sock.sendall((json.dumps(state) + "\n").encode())
    time.sleep(0.2)

# 遊戲結束
final_score = {"type":"GAME_OVER", "score":1000}
sock.sendall((json.dumps(final_score)+"\n").encode())

# 接收伺服器結果
for line in recv_lines(sock):
    if line in ["WIN","LOSE","DRAW"]:
        print("Result from server:", line)
        break

sock.close()
