import asyncio
import itertools
import json
import logging

import websockets
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from game.board import Board
from server.engine.lobby import handle_leave
from server.models.player import Player
from server.models.room import Room

logging.basicConfig(level=logging.DEBUG)

room = Room()
_player_id_counter = itertools.count()


async def handler(ws: ServerConnection):
    player_id = next(_player_id_counter)
    room.connections[ws] = Player(Board(room.shared_bag), player_id)
    room.connections[ws].outbox.append(("room_state", {"state": room.state.value}))
    room.broadcast_lobby()

    try:
        async for msg in ws:
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                await ws.close(1003)
                return
            if not isinstance(data, dict):
                await ws.close(1003)
                return
            await room.handle_message(ws, data)
    except ConnectionClosed:
        pass
    finally:
        await handle_leave(room, ws)


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8888):
        await asyncio.gather(room.game_loop(), room.net_loop())


if __name__ == "__main__":
    asyncio.run(main())
