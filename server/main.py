from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from server.db.models import user as _user  # noqa: F401  (registers the table)
from server.db.session import Base, engine
from server.errors import AppError
from server.routes import auth, health, rooms, ws
from server.services.room_manager import RoomManager
import time
from sqlalchemy.exc import OperationalError

MAX_RETRIES = 5
RETRY_INTERVAL = 2

@asynccontextmanager
async def lifespan(_app: FastAPI):
    for attempt in range(MAX_RETRIES):
        try:
            Base.metadata.create_all(bind=engine)
            print("Database connected and tables created successfully!")
            break
        except OperationalError as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Database not ready yet (attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {RETRY_INTERVAL}s...")
                time.sleep(RETRY_INTERVAL)
            else:
                print("Could not connect to the database. Exiting.")
                raise e
    room_manager = RoomManager()

    yield {"room_manager": room_manager}

    for host in list(room_manager.rooms):
        await room_manager.delete_room(host)


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
