import asyncio
import json
import random
import time
from statistics import mean

HOST = "127.0.0.1"
PORT = 5000

TOTAL_PLAYERS = 60
ROOM_SIZE = 2
TIMEOUT = 10  # seconds


# --------- 統計資料 ---------
results = {
    "success": 0,
    "failure": 0,
    "join_to_start": [],
    "start_to_result": [],
    "join_to_result": [],
}


async def fake_player(player_id: int, room_id: str):
    join_time = None
    start_time = None

    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)

        # JOIN
        join_time = time.perf_counter()
        writer.write(f"ROOM {room_id}\n".encode())
        await writer.drain()

        while True:
            try:
                line = await asyncio.wait_for(reader.readline(), timeout=TIMEOUT)
                if not line:
                    raise RuntimeError("server closed")

                msg = line.decode().strip()

                # ---- 失敗條件 ----
                if msg in ("ROOM_FULL", "NO_OPPONENT"):
                    raise RuntimeError(msg)

                # ---- 遊戲開始 ----
                if msg == "START":
                    start_time = time.perf_counter()
                    results["join_to_start"].append(start_time - join_time)

                    # 模擬遊戲中資料
                    for i in range(5):
                        payload = {
                            "type": "GAME_DATA",
                            "tick": i,
                            "player": player_id
                        }
                        writer.write((json.dumps(payload) + "\n").encode())
                        await writer.drain()
                        await asyncio.sleep(random.uniform(0.05, 0.15))

                    # GAME OVER
                    score = random.randint(0, 100)
                    writer.write(
                        (json.dumps({"type": "GAME_OVER", "score": score}) + "\n").encode()
                    )
                    await writer.drain()
                    continue

                # ---- 結果 ----
                try:
                    payload = json.loads(msg)
                except json.JSONDecodeError:
                    continue

                if payload.get("type") == "GAME_RESULT":
                    end_time = time.perf_counter()

                    results["start_to_result"].append(end_time - start_time)
                    results["join_to_result"].append(end_time - join_time)
                    results["success"] += 1
                    break

            except asyncio.TimeoutError:
                raise RuntimeError("timeout")

            except Exception as e:
                raise RuntimeError(f"error: {e}")

        writer.close()
        await writer.wait_closed()

    except Exception as e:
        results["failure"] += 1
        # 你要 debug 可以打開
        print(f"[P{player_id}] FAIL: {e}")


async def main():
    start = time.perf_counter()

    tasks = []
    for i in range(TOTAL_PLAYERS):
        room_id = f"room_{i // ROOM_SIZE}"
        tasks.append(fake_player(i, room_id))

    await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start

    # --------- 統計輸出 ---------
    total = results["success"] + results["failure"]

    print("\n========== STRESS TEST RESULT ==========")
    print(f"Total players      : {total}")
    print(f"Success            : {results['success']}")
    print(f"Failure            : {results['failure']}")
    print(f"Success rate       : {results['success'] / total * 100:.2f}%")
    print(f"Elapsed time       : {elapsed:.2f}s")

    if results["join_to_start"]:
        print("\n--- Latency (seconds) ---")
        print(f"Join → START avg   : {mean(results['join_to_start']):.4f}")
        print(f"START → RESULT avg : {mean(results['start_to_result']):.4f}")
        print(f"Join → RESULT avg  : {mean(results['join_to_result']):.4f}")


if __name__ == "__main__":
    asyncio.run(main())
