import logging

from net.protocol import broadcast_json, send_json

logging.basicConfig(level=logging.DEBUG)

import asyncio
import json
import websockets
import random

from server.match import Match, MatchState
from websockets.asyncio.server import ServerConnection
from game.board import Board
from net.client import Client

match = Match()


async def handler(ws: ServerConnection):
    id = random.randint(0, 1000)
    match.connections[ws] = Client(Board(match.shared_bag), id)
    await send_json(ws, "match_state", {"state": MatchState.WAITING.value, "player_count": len(match.connections)})
    await broadcast_json(match, "player_joined", None, [ws])

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
