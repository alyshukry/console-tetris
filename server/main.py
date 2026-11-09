from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from server.errors import AppError
from server.routes import health, rooms, ws, auth
from server.services.room_manager import RoomManager
from server.db import Base, engine
from server.models import user as _user  # noqa: F401  (registers the table)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(engine)
    room_manager = RoomManager()

    yield {"room_manager": room_manager}

    for host in list(room_manager.rooms):
        await room_manager.delete_room(host)
    print("Closing server")


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(ws.router)
app.include_router(rooms.router)
app.include_router(auth.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}, headers=headers
    )
