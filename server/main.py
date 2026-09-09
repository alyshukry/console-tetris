import asyncio
import curses
import json
import websockets
import random

from websockets.asyncio.server import ServerConnection
from game.board import Board
from game.seven_bag import SevenBag
from net.client import Client
from net.protocol import send_json

connections: dict[ServerConnection, Client] = {}

async def game_loop():
    while True:
        for client in connections.values():
            if not client.board.game_over:
                client.board.move_piece_down()
        await asyncio.sleep(0.5)

async def net_loop():
    while True:
        for ws, client in list(connections.items()):
            await send_json(
                ws,
                "all_boards",
                {
                    "boards": {
                        client.id: client.board.to_dict()
                        for _, client in connections.items()
                    }
                },
            )
        await asyncio.sleep(0.05)


shared_bag = SevenBag()
async def handler(ws: ServerConnection):
    board = Board(shared_bag)

    id = random.randint(0, 1000)
    connections[ws] = Client(board, id)

    await send_json(ws, "welcome_info", {"your_board": board.to_dict(), "your_id": id})
    for ws, _ in list(connections.items()):
        await send_json(
            ws,
            "all_boards",
            {
                "boards": {
                    client.id: client.board.to_dict()
                    for _, client in connections.items()
                }
            },
            )

    try:
        async for msg in ws:
            data = json.loads(msg)
            print(f"from client[{connections[ws].id}]: {data}")

            match data.get("type"):
                case "input":
                    if not connections[ws].board.game_over:
                        key = data.get("key")
                        print(data)
                        if key == curses.KEY_LEFT:
                            connections[ws].board.move_piece_left()
                        elif key == curses.KEY_RIGHT:
                            connections[ws].board.move_piece_right()
                        elif key == curses.KEY_UP:
                            connections[ws].board.rotate_piece()
                        elif key == curses.KEY_DOWN:
                            connections[ws].board.move_piece_down()
                        elif key == ord(" "):
                            connections[ws].board.drop_piece()
                case _:
                    pass
    finally:
        del connections[ws]


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8888):
        await asyncio.gather(game_loop(), net_loop())


asyncio.run(main())
