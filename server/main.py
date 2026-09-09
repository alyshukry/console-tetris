import logging

logging.basicConfig(level=logging.DEBUG)

import asyncio
import curses
import json
import websockets
import random

from websockets.asyncio.server import ServerConnection
from game.board import Board
from game.garbage import send_garbage
from game.seven_bag import SevenBag
from net.client import Client
from net.protocol import send_json
from enum import Enum, auto


class MatchState(Enum):
    WAITING = auto()  # lobby, waiting for ready-ups
    IN_PROGRESS = auto()  # game_loop/net_loop active
    FINISHED = auto()  # someone won, results shown


connections: dict[ServerConnection, Client] = {}
match_state = MatchState.WAITING
game_ready = asyncio.Event()


async def check_ready():
    global match_state
    if (
        match_state == MatchState.WAITING
        and connections
        and all(c.ready for c in connections.values())
    ):
        await start_game()


async def start_game():
    global match_state
    for client in connections.values():
        board = client.board

        def on_lines_cleared(
            lines: int, board=board
        ):  # default arg to avoid late-binding bug
            send_garbage(
                board,
                [c.board for c in connections.values() if c.board is not board],
                lines,
            )

        board.on_lines_cleared = on_lines_cleared

    for ws, client in connections.items():
        await send_json(
            ws,
            "welcome_info",
            {"your_board": client.board.to_dict(), "your_id": client.id},
        )
        await send_json(
            ws,
            "all_boards",
            {"boards": {c.id: c.board.to_dict() for c in connections.values()}},
        )
        
    match_state = MatchState.IN_PROGRESS
    game_ready.set()


async def game_loop():
    await game_ready.wait()
    while True:
        if match_state == MatchState.IN_PROGRESS:
            for client in connections.values():
                if not client.board.game_over:
                    client.board.move_piece_down()
            await asyncio.sleep(0.5)


async def net_loop():
    await game_ready.wait()
    while True:
        if match_state == MatchState.IN_PROGRESS:
            for ws, _ in list(connections.items()):
                await send_json(
                    ws,
                    "all_boards",
                    {"boards": {c.id: c.board.to_dict() for c in connections.values()}},
                )
            await asyncio.sleep(0.05)


shared_bag = SevenBag()


async def handler(ws: ServerConnection):
    id = random.randint(0, 1000)
    connections[ws] = Client(Board(shared_bag), id)

    try:
        async for msg in ws:
            data = json.loads(msg)

            match data.get("type"):
                case "input":
                    if connections[ws].board and not connections[ws].board.game_over:
                        key = data.get("key")
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
                case "ready":
                    connections[ws].ready = True
                    await check_ready()
                case _:
                    pass
    finally:
        del connections[ws]


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8888):
        await asyncio.gather(game_loop(), net_loop())


asyncio.run(main())
