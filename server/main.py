import asyncio
import itertools
import json
import logging

import websockets
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from game.board import Board
from net.protocol import broadcast_json, send_json
from server.player import Player
from server.room import Room
from shared.room_state import RoomState

logging.basicConfig(level=logging.DEBUG)

room = Room()
_player_id_counter = itertools.count()


async def handler(ws: ServerConnection):
    player_id = next(_player_id_counter)
    room.connections[ws] = Player(Board(room.shared_bag), player_id)
    await send_json(
        ws,
        "room_state",
        {
            "state": RoomState.LOBBY.value,
            "player_count": len(room.connections),
            "ready_count": sum(p.ready for p in room.connections.values()),
        },
    )
    await broadcast_json(room, "player_joined", None, [ws])

    try:
        async for msg in ws:
            data = json.loads(msg)
            await room.handle_message(ws, data)
    except ConnectionClosed:
        pass
    finally:
        leaver = room.connections.pop(ws, None)
        if leaver:
            await broadcast_json(
                room,
                "player_left",
                {"player_id": leaver.player_id, "was_ready": leaver.ready},
            )


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8888):
        await asyncio.gather(room.game_loop(), room.net_loop())


if __name__ == "__main__":
    asyncio.run(main())
