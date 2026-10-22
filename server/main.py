import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from server.errors import AppError
from server.routes import health, ws, rooms
from server.security import hash_password
from server.services.room_manager import RoomManager

logging.basicConfig(level=logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    room_manager = RoomManager()
    room_manager.create_room("hilo", hash_password("supersecret"))

    yield {"room_manager": room_manager}

    print("closing")


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(ws.router)
app.include_router(rooms.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
