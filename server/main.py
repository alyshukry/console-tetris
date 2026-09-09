import logging

logging.basicConfig(level=logging.DEBUG)

import asyncio
import json
import websockets
import random

from server.match import Match
from websockets.asyncio.server import ServerConnection
from game.board import Board
from net.client import Client
from enum import Enum, auto


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
