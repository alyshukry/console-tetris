import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from server.routes import health, ws
from server.services.room_manager import RoomManager

logging.basicConfig(level=logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.room_manager = RoomManager()
    app.state.room_manager.create_room("hilo")

    yield
    print("closing")

app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(ws.router)
