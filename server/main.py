import asyncio
from contextlib import asynccontextmanager, suppress
import logging

from fastapi import FastAPI

from server.engine.loop import run_rooms
from server.models.room import Room
from server.routes import health, ws
from server.services.room_manager import RoomManager

logging.basicConfig(level=logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.room_manager = RoomManager()
    app.state.room_manager.rooms["hi"] = Room()
    room_task = asyncio.create_task(run_rooms(app.state.room_manager.rooms))

    try:
        yield
    finally:
        room_task.cancel()
        with suppress(asyncio.CancelledError):
            await room_task


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(ws.router)
