import asyncio
import json
import websockets
import curses

from game.board import Board
from render.curses_render import draw, setup_curses


def main(stdscr):
    setup_curses(stdscr)
    
    boards: dict[int, Board] = {}
    my_id: int = -1

    async def run_client():
        async with websockets.connect("ws://localhost:8888") as ws:
            print("connected")
            await ws.send("hello server")
            
            async def input_loop():
                while True:
                    key = stdscr.getch()
                    if key != -1: await ws.send(str({"input": key}))

                    await asyncio.sleep(0.05)

            async def receive_loop():
                nonlocal boards, my_id
                async for msg in ws:
                    data = json.loads(msg)
                    print(f"from server: {data}")
                    if data["type"] == "welcome_info":
                        my_id = data["your_id"]
                    if data["type"] == "all_boards":
                        boards = data["boards"]
                    
                    x, y = 0, 0
                    for id, board in boards.items():
                        draw(board, x, y, True if id == my_id else False, stdscr)
                        x += 20

            await asyncio.gather(input_loop(), receive_loop())
    asyncio.run(run_client())


curses.wrapper(main)
