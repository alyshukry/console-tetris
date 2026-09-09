import asyncio
import json
import websockets
import curses

from game.board import Board
from net.protocol import send_json
from render.curses_render import draw, setup_curses


def draw_boards(boards, stdscr, my_id):
    x = 1
    y = 1 + draw(boards[my_id], stdscr, 1, 1, True)[1] + 1
    for id, board in boards.items():
        if id != my_id:
            y += draw(board, stdscr, x, y, False)[1]


def main(stdscr):
    setup_curses(stdscr)

    boards: dict[int, dict] = {}
    my_id: int = -1

    async def run_client():
        async with websockets.connect("ws://localhost:8888") as ws:
            print("connected")

            async def input_loop():
                while True:
                    key = stdscr.getch()
                    if key != -1:
                        await send_json(ws, "input", {"key": key})
                    
                    if key == ord("k"): await send_json(ws, "ready")

                    await asyncio.sleep(0.05)

            async def receive_loop():
                nonlocal boards, my_id
                async for msg in ws:
                    data = json.loads(msg)
                    print(f"from server: {data}")

                    match data["type"]:
                        case "welcome_info":
                            my_id = data["your_id"]
                        case "all_boards":
                            boards = {int(k): v for k, v in data["boards"].items()}

                    if my_id in boards:
                        draw_boards(boards, stdscr, my_id)

            await asyncio.gather(input_loop(), receive_loop())

    asyncio.run(run_client())


curses.wrapper(main)
