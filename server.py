import socket
import threading
import json
import time

HOST = "0.0.0.0"    # 允許所有 IP 連線
PORT = 5000

rooms = {}          # room_id -> [conn1, conn2]
client_room = {}    # conn -> room_id
final_scores = {}   # room_id -> {conn: score}  


def relay(sender, room_id, data):     # 傳輸資料
    for c in rooms.get(room_id, []):
        if c != sender:
            c.sendall(data + b'\n')

def handle_client(conn, addr):        #處裡用戶
    room_id = None
    buffer = ""

    try:
        while True:
            data = conn.recv(8192)    # 接收資料包 (一次最多傳遞 8192 bytes)
            if not data:
                print(f"[DISCONNECT] {addr} (client closed connection)")
                break

            buffer += data.decode()       # 把 bytes 轉為 str

            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)

                # ---- join room ----
                if msg.startswith("ROOM"):  # 若 client 輸入"ROOM 1234"，分離出 "1234" 作為房號
                    _, room_id = msg.split()
                    rooms.setdefault(room_id, []).append(conn) # 若沒有該房間則創建該房間
                    client_room[conn] = room_id
                    print(f"[ROOM] {addr} joined room {room_id}")

                    start_time = time.time()
                    while len(rooms[room_id]) < 2:
                        if time.time() - start_time > 15:
                            print(f"[TIMEOUT] Room {room_id} only has 1 player")
                            conn.sendall(b"NO_OPPONENT\n")
                            break
                        time.sleep(0.1)

                    if len(rooms[room_id]) == 2:
                        for c in rooms[room_id]:
                            c.sendall(b"START\n")

                else:
                    payload = json.loads(msg) # 解析 json

                    # ---- game over ----
                    if payload.get("type") == "GAME_OVER":
                        final_scores.setdefault(room_id, {})[conn] = payload["score"]

                        # 兩人都結束 → 判斷勝負
                        if len(final_scores[room_id]) == 2:
                            (c1, s1), (c2, s2) = final_scores[room_id].items()

                            if s1 > s2:
                                c1.sendall(b"WIN\n")
                                c2.sendall(b"LOSE\n")
                            elif s1 < s2:
                                c1.sendall(b"LOSE\n")
                                c2.sendall(b"WIN\n")
                            else:
                                c1.sendall(b"DRAW\n")
                                c2.sendall(b"DRAW\n")

                    # ---- relay normal state ----
                    else:
                        relay(conn, room_id, data)

    finally: # 不管有沒有錯都會執行
        print(f"[DISCONNECT] {addr}")
        if room_id and conn in rooms.get(room_id, []): # 移除房間裡的 client
            rooms[room_id].remove(conn)
        conn.close()


# ---- main ----
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
server.settimeout(1.0)  # 設定 accept 最多等 1 秒

print("Server started")

try:
    while True: # 阻塞式等待連線，因此要獨立出來
        try:
            conn, addr = server.accept() # 等待用戶端進入 (conn → client 的 socket 連線物件，addr → client 的 IP 和 port)
            threading.Thread(
                target = handle_client, # 要執行的函式
                args = (conn, addr),    # 傳給 handle_client 的參數
                daemon = True           # 主程式結束就會自動殺掉
            ).start()                 # 啟動這個線程
        except socket.timeout:
            continue  # 1 秒沒有連線就回到 while True，這樣可以捕捉 Ctrl+C
except KeyboardInterrupt:
    print("\n[SERVER] KeyboardInterrupt, shutting down...")
finally:
    server.close()