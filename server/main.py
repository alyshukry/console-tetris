import asyncio
import logging

from fastapi import FastAPI
import websockets

from server.engine.loop import run_room
from server.routes.ws import handler, room
from server.routes import health

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()


async def main():
    app.include_router(health.router)

    async with websockets.serve(handler, "0.0.0.0", 8888):
        await run_room(room)


if __name__ == "__main__":
    asyncio.run(main())
