import asyncio
import itertools
import json
import logging

import websockets
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from game.board import Board
from server.engine.lobby import handle_leave
from server.engine.loop import run_room
from server.models.player import Player
from server.models.room import Room
from server.routes.ws import handle_message
from server.handler import room

logging.basicConfig(level=logging.DEBUG)


async def main():
    await run_room(room)


if __name__ == "__main__":
    asyncio.run(main())
