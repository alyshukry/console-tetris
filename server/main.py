from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from server.errors import AppError
from server.routes import health, rooms, ws
from server.services.room_manager import RoomManager


@asynccontextmanager
async def lifespan(_app: FastAPI):
    room_manager = RoomManager()

    yield {"room_manager": room_manager}

    for host in list(room_manager.rooms):
        await room_manager.delete_room(host)
    print("Closing server")


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(ws.router)
app.include_router(rooms.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
