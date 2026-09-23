import logging

from net.protocol import broadcast_json, send_json

logging.basicConfig(level=logging.DEBUG)

import asyncio
import json
import websockets
import itertools

from server.match import Match, MatchState
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed
from game.board import Board
from net.client import Client

match = Match()
_id_counter = itertools.count()

async def handler(ws: ServerConnection):
    id = next(_id_counter)
    match.connections[ws] = Client(Board(match.shared_bag), id)
    await send_json(
        ws,
        "match_state",
        {
            "state": MatchState.LOBBY.value,
            "player_count": len(match.connections),
            "ready_count": sum(c.ready for c in match.connections.values()),
        },
    )
    await broadcast_json(match, "player_joined", None, [ws])

    try:
        async for msg in ws:
            data = json.loads(msg)
            await match.handle_message(ws, data)
    except ConnectionClosed:
        pass
    finally:
        leaver = match.connections.pop(ws, None)
        if leaver:
            await broadcast_json(
                match,
                "player_left",
                {"player_id": leaver.id, "was_ready": leaver.ready},
            )


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8888):
        await asyncio.gather(match.game_loop(), match.net_loop())


asyncio.run(main())
