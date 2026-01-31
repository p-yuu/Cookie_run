import asyncio
import json

HOST = "0.0.0.0"
PORT = 5000

rooms: dict[str, list[asyncio.StreamWriter]] = {} # room_id -> [writer1, writer2]
room_events: dict[str, asyncio.Event] = {} # room_id -> asyncio.Event (避免 busy wait)
final_scores: dict[str, dict[asyncio.StreamWriter, int]] = {} # room_id -> {writer: score}


async def safe_write(writer: asyncio.StreamWriter, data: bytes):
    # 避免對方斷線、關閉等error
    try:
        writer.write(data)
        await writer.drain()
        return True
    except Exception:
        return False


async def relay(sender, room_id, data: bytes):
    # 把資料轉發給房間內另一位玩家
    for w in rooms.get(room_id, []).copy():
        if w is sender:
            continue
        ok = await safe_write(w, data + b"\n")
        if not ok:
            print(f"[REMOVE] {w.get_extra_info('peername')} disconnected during relay")
            rooms[room_id].remove(w)

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    room_id = None
    print(f"[CONNECT] {addr}")

    try:
        while True:
            line = await reader.readline()
            if not line:
                break
            msg = line.decode().strip()

            # ---------- JOIN ROOM ----------
            if msg.startswith("ROOM"):
                _, rid = msg.split(maxsplit=1)

                # 已經在房間就忽略
                if room_id is not None:
                    continue

                rooms.setdefault(rid, [])
                room_events.setdefault(rid, asyncio.Event())

                # 房間已滿 → 擋掉
                if len(rooms[rid]) >= 2:
                    await safe_write(writer, b"ROOM_FULL\n")
                    print(f"[ROOM] {addr} tried to join {rid}, but room is full")
                    continue

                room_id = rid
                # 防止同一個 writer 被加兩次
                if writer not in rooms[room_id]:
                    rooms[room_id].append(writer)
                print(f"[ROOM] {addr} joined {room_id}")

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
                        await asyncio.wait_for(room_events[room_id].wait(), timeout=15) # 等待
                    except asyncio.TimeoutError:
                        await safe_write(writer, b"NO_OPPONENT\n")
                        rooms[room_id].remove(writer)
                        if not rooms[room_id]:
                            rooms.pop(room_id, None)
                            room_events.pop(room_id, None)
                        room_id = None
                        break

            # ---------- GAME DATA ----------
            else:
                try:
                    payload = json.loads(msg)
                except json.JSONDecodeError:
                    if room_id:
                        await relay(writer, room_id, msg.encode())
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
                        final_scores.pop(room_id, None)
                        rooms.pop(room_id, None)
                        room_events.pop(room_id, None)
                        room_id = None
                        break

                # ---------- RELAY ----------
                else:
                    if room_id:
                        await relay(writer, room_id, msg.encode())

    except Exception as e:
        print(f"[ERROR] {addr} {e}")

    finally:
        print(f"[DISCONNECT] {addr}")

        # 通知對手
        if room_id and room_id in rooms:
            for w in rooms[room_id]:
                if w is not writer:
                    await safe_write(w, b'{"type":"OPPONENT_LEFT"}\n')

        # 清理資料
        if room_id:
            if room_id in rooms and writer in rooms[room_id]:
                rooms[room_id].remove(writer)
            if room_id in rooms and not rooms[room_id]:
                rooms.pop(room_id, None)
                room_events.pop(room_id, None)
            if room_id in final_scores:
                final_scores[room_id].pop(writer, None)

        writer.close()
        try:
            await writer.wait_closed()
        except ConnectionResetError:
            pass


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"[SERVER] running on {HOST}:{PORT}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())