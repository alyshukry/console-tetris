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


class Match:
    def __init__(self):
        self.connections: dict[ServerConnection, Client] = {}
        self.state = MatchState.WAITING
        self.all_ready = asyncio.Event()
        self.shared_bag = SevenBag()

    def all_boards_payload(self):
        return {"boards": {c.id: c.board.to_dict() for c in self.connections.values()}}

    async def check_ready(self):
        if (
            self.state == MatchState.WAITING
            and self.connections
            and all(c.ready for c in self.connections.values())
        ):
            await self.start_game()

    async def start_game(self):
        for client in self.connections.values():
            board = client.board

            def on_lines_cleared(lines: int, board=board):
                send_garbage(
                    board,
                    [
                        c.board
                        for c in self.connections.values()
                        if c.board is not board
                    ],
                    lines,
                )

            board.on_lines_cleared = on_lines_cleared

        for ws, client in self.connections.items():
            await send_json(
                ws,
                "welcome_info",
                {"your_board": client.board.to_dict(), "your_id": client.id},
            )
            await send_json(ws, "all_boards", self.all_boards_payload())

        self.state = MatchState.IN_PROGRESS
        self.all_ready.set()

    async def game_loop(self):
        await self.all_ready.wait()
        while True:
            if self.state == MatchState.IN_PROGRESS:
                for client in self.connections.values():
                    if not client.board.game_over:
                        client.board.move_piece_down()
                await asyncio.sleep(0.5)

    async def net_loop(self):
        await self.all_ready.wait()
        while True:
            if self.state == MatchState.IN_PROGRESS:
                for ws in list(self.connections):
                    await send_json(ws, "all_boards", self.all_boards_payload())
                await asyncio.sleep(0.05)

    async def handle_message(self, ws, data):
        client = self.connections[ws]
        match data.get("type"):
            case "input":
                handle_input(client, data.get("key"))
            case "ready":
                client.ready = True
                await self.check_ready()


def handle_input(client: Client, key):
    if client.board.game_over:
        return
    {
        curses.KEY_LEFT: client.board.move_piece_left,
        curses.KEY_RIGHT: client.board.move_piece_right,
        curses.KEY_UP: client.board.rotate_piece,
        curses.KEY_DOWN: client.board.move_piece_down,
        ord(" "): client.board.drop_piece,
    }.get(key, lambda: None)()


match = Match()

async def handler(ws: ServerConnection):
    id = random.randint(0, 1000)
    match.connections[ws] = Client(Board(match.shared_bag), id)

    try:
        async for msg in ws:
            data = json.loads(msg)
            await match.handle_message(ws, data)
    finally:
        del match.connections[ws]


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8888):
        await asyncio.gather(match.game_loop(), match.net_loop())


asyncio.run(main())
