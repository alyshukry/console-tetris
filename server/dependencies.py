from typing import Annotated

from fastapi import Depends
from starlette.requests import HTTPConnection

from server.services.room_manager import RoomManager


def get_room_manager(conn: HTTPConnection) -> RoomManager:
    return conn.state.room_manager


RoomManagerDep = Annotated[RoomManager, Depends(get_room_manager)]
