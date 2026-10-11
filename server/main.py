import asyncio
import logging

from server.engine.loop import run_room
from server.routes.ws import room

logging.basicConfig(level=logging.DEBUG)


async def main():
    await run_room(room)


if __name__ == "__main__":
    asyncio.run(main())
