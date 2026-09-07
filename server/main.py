import asyncio
import websockets
import random

from websockets.asyncio.server import ServerConnection
from game.board import Board
from game.seven_bag import SevenBag
from net.protocol import send_json

connections: dict[ServerConnection, Board] = {}
client_ids: dict[ServerConnection, int] = {}


async def game_loop():
    while True:
        for board in connections.values():
            if not board.game_over:
                board.move_piece_down()
        await asyncio.sleep(0.5)
        for ws, board in list(connections.items()):
            await send_json(
                ws,
                "all_boards",
                {
                    "boards": {
                        client_ids[client_ws]: client_board.to_dict()
                        for client_ws, client_board in connections.items()
                    }
                },
            )


async def handler(ws: ServerConnection):
    shared_bag = SevenBag()
    board = Board(shared_bag)

    id = random.randint(0, 1000)
    client_ids[ws] = id
    connections[ws] = board

    await send_json(ws, "welcome_info", {"your_board": board.to_dict(), "your_id": id})
    await send_json(
        ws,
        "all_boards",
        {
            "boards": {
                client_ids[client_ws]: client_board.to_dict()
                for client_ws, client_board in connections.items()
            }
        },
    )

    try:
        async for msg in ws:
            print(f"from client[{client_ids[ws]}]: {msg}")
    finally:
        del connections[ws]
        del client_ids[ws]


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8888):
        asyncio.create_task(game_loop())
        await asyncio.Future()


asyncio.run(main())
