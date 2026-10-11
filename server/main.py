import asyncio
import logging

import websockets

from server.engine.loop import run_room
from server.routes.ws import handler, room

logging.basicConfig(level=logging.DEBUG)


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8888):
        await run_room(room)


if __name__ == "__main__":
    asyncio.run(main())
