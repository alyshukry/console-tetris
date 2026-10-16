import asyncio
import logging

from fastapi import FastAPI
import websockets

from server.engine.loop import run_room
from server.routes.ws import room
from server.routes import health
from server.routes import ws

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
app.include_router(health.router)
app.include_router(ws.ws_endpoint)


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8888):
        await run_room(room)


if __name__ == "__main__":
    asyncio.run(main())
