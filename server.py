import asyncio
import json
import time

HOST = "0.0.0.0"
PORT = 5000

ROOM_TTL = 30          # 房間 30 秒沒活動就刪
PING_TIMEOUT = 15      # client 超過 15 秒沒 ping 視為斷線
DEBUG_INTERVAL = 5     # debug 每 5 秒印一次
DEBUG = True

rooms = {} # room_id -> [writer1, writer2]
room_events = {} # room_id -> asyncio.Event (避免 busy wait)
final_scores = {} # room_id -> {writer: score}
room_last_active = {}  # room_id -> timestamp
writer_last_ping = {}  # writer -> timestamp

# TTL
async def watchdog():
    while True:
        now = time.time()

        # writer 心跳
        for w, t in list(writer_last_ping.items()):
            if now - t > PING_TIMEOUT:
                print("[WATCHDOG] writer timeout")
                for rid, ws in list(rooms.items()):
                    if w in ws:
                        remove_writer(w, rid)

        # room TTL
        for rid, t in list(room_last_active.items()):
            if now - t > ROOM_TTL:
                print(f"[WATCHDOG] room {rid} expired")
                for w in rooms.get(rid, []):
                    await safe_write(w, b'{"type":"OPPONENT_LEFT"}\n')
                    remove_writer(w, rid)
                rooms.pop(rid, None)
                room_events.pop(rid, None)
                final_scores.pop(rid, None)
                room_last_active.pop(rid, None)

        await asyncio.sleep(3)

# log / debug
async def debug_monitor():
    while True:
        print("\n[DEBUG STATUS]")
        for rid, ws in rooms.items():
            print(f" room {rid}: {len(ws)} player(s)")
        print("------------------")
        await asyncio.sleep(DEBUG_INTERVAL)

def reset_all():
    rooms.clear()
    room_events.clear()
    final_scores.clear()
    room_last_active.clear()
    writer_last_ping.clear()
    print("[INIT] server state cleared")

# 移除 writer
def remove_writer(writer, room_id):
    if room_id in rooms and writer in rooms[room_id]:
        rooms[room_id].remove(writer)

    writer_last_ping.pop(writer, None)
    final_scores.get(room_id, {}).pop(writer, None)

    if room_id in rooms and not rooms[room_id]:
        rooms.pop(room_id, None)
        room_events.pop(room_id, None)
        room_last_active.pop(room_id, None)
        final_scores.pop(room_id, None)
    else: # 確保等待時不會 deadlock
        if room_id in room_events:
            room_events[room_id].set()

# 安全寫入
async def safe_write(writer: asyncio.StreamWriter, data: bytes):
    try:
        writer.write(data)
        await writer.drain()
        return True
    except Exception:
        remove_writer(writer, None)
        return False

# 轉發資料
async def relay(sender, room_id, data: bytes):
    for w in rooms.get(room_id, []).copy():
        if w is sender:
            continue
        ok = await safe_write(w, data + b"\n")
        if not ok:
            print(f"[REMOVE] {w.get_extra_info('peername')} disconnected during relay")
            rooms[room_id].remove(w)

async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    room_id = None
    print(f"[CONNECT] {addr}")

    try:
        while True:
            line = await reader.readline()
            if not line:
                break
            msg = line.decode().strip()
            writer_last_ping[writer] = time.time()
            if room_id:
                room_last_active[room_id] = time.time()

            # ---------- JOIN ROOM ----------
            if msg.startswith("ROOM"):
                _, rid = msg.split(maxsplit=1)

                # 已經在房間就忽略
                if room_id is not None:
                    continue

                rooms.setdefault(rid, [])
                room_events.setdefault(rid, asyncio.Event())
                room_last_active[rid] = time.time()

                # 房間已滿
                if len(rooms[rid]) >= 2:
                    await safe_write(writer, b"ROOM_FULL\n")
                    print(f"[ROOM] {addr} tried to join {rid}, but room is full")
                    continue

                room_id = rid
                rooms[rid].append(writer)
                print(f"[ROOM] {addr} joined {rid}")

                # 第二人到齊 → 啟動
                if len(rooms[room_id]) == 2:
                    alive = []
                    for w in rooms[room_id].copy():
                        ok = await safe_write(w, b"START\n")
                        print(f"[ROOM] {room_id} START sent to 2 players") ##
                        if ok:
                            alive.append(w)
                        else:
                            print(f"[REMOVE] {w.get_extra_info('peername')} disconnected before START")
                    rooms[room_id] = alive

                    if len(alive) < 2:
                        for w in alive:
                            await safe_write(w, b"NO_OPPONENT\n")
                        rooms.pop(room_id, None)
                        room_events.pop(room_id, None)
                        room_id = None
                        break

                    room_events[room_id].set()
                else:
                    try:
                        await asyncio.wait_for(room_events[rid].wait(), timeout=ROOM_TTL)
                        if room_id not in rooms:
                            await safe_write(writer, b"NO_OPPONENT\n")
                            remove_writer(writer, rid)
                            break
                    except asyncio.TimeoutError:
                        await safe_write(writer, b"NO_OPPONENT\n")
                        remove_writer(writer, rid)
                        break

            # ---------- GAME DATA ----------
            else:
                try:
                    payload = json.loads(msg)
                except json.JSONDecodeError:
                    if room_id:
                        await relay(writer, room_id, msg.encode())
                    continue

                # ---------- HEARTBEAT ----------
                if payload.get("type") == "PING":
                    print("[PING]", addr) ##
                    continue

                # ---------- GAME OVER ----------
                if payload.get("type") == "GAME_OVER":
                    final_scores.setdefault(room_id, {})

                    # 防止重複送
                    if writer in final_scores[room_id]:
                        continue

                    final_scores[room_id][writer] = payload["score"]

                    # 兩人都結束 → 判定
                    if len(final_scores[room_id]) == 2:
                        (w1, s1), (w2, s2) = final_scores[room_id].items()

                        if s1 > s2:
                            r1 = {"type": "GAME_RESULT", "RESULT": "WIN", "MY_SCORE": s1, "OPP_SCORE": s2}
                            r2 = {"type": "GAME_RESULT", "RESULT": "LOSE", "MY_SCORE": s2, "OPP_SCORE": s1}
                        elif s1 < s2:
                            r1 = {"type": "GAME_RESULT", "RESULT": "LOSE", "MY_SCORE": s1, "OPP_SCORE": s2}
                            r2 = {"type": "GAME_RESULT", "RESULT": "WIN", "MY_SCORE": s2, "OPP_SCORE": s1}
                        else:
                            r1 = r2 = {"type": "GAME_RESULT", "RESULT": "DRAW", "MY_SCORE": s1, "OPP_SCORE": s2}

                        await safe_write(w1, (json.dumps(r1) + "\n").encode())
                        await safe_write(w2, (json.dumps(r2) + "\n").encode())

                        # 清理
                        remove_writer(w1, room_id)
                        remove_writer(w2, room_id)
                        break

                # ---------- RELAY ----------
                else:
                    if room_id:
                        await relay(writer, room_id, msg.encode())

    except Exception as e:
        print(f"[ERROR] {addr} {e}")

    finally:
        print(f"[DISCONNECT] {addr}")
        if room_id:
            remove_writer(writer, room_id)
        try:
            writer.close()
            await writer.wait_closed()
        except (ConnectionResetError, BrokenPipeError):
            pass

async def main():
    reset_all()
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"[SERVER] running on {HOST}:{PORT}")

    asyncio.create_task(watchdog())
    if DEBUG:
        asyncio.create_task(debug_monitor())

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())