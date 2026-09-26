import asyncio
import itertools
import json
import logging

import websockets
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from game.board import Board
from server.player import Player
from net.protocol import broadcast_json, send_json
from server.match import Match, MatchState

logging.basicConfig(level=logging.DEBUG)

match = Match()
_id_counter = itertools.count()


async def handler(ws: ServerConnection):
    id = next(_id_counter)
    match.connections[ws] = Player(Board(match.shared_bag), id)
    await send_json(
        ws,
        "match_state",
        {
            "state": MatchState.LOBBY.value,
            "player_count": len(match.connections),
            "ready_count": sum(p.ready for p in match.connections.values()),
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


if __name__ == "__main__":
    asyncio.run(main())
