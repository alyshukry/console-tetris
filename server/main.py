
import asyncio
from contextlib import asynccontextmanager, suppress
import logging

from fastapi import FastAPI

from server.engine.loop import run_room
from server.routes import health, ws

logging.basicConfig(level=logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    room_task = asyncio.create_task(run_room(ws.room))

    try:
        yield
    finally:
        room_task.cancel()
        with suppress(asyncio.CancelledError):
            await room_task


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(ws.router)
