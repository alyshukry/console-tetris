from typing import Annotated

from fastapi import APIRouter, Depends, Request

from server.dependencies import get_room_manager
from server.errors import AppError
from server.security import hash_password
from server.schemas.rooms import CreateRoomRequest, RoomSummary
from server.services.room_manager import RoomManager

router = APIRouter()


@router.post("/rooms", status_code=201, response_model=RoomSummary)
async def create_room(
    body: CreateRoomRequest,
    room_manager: Annotated[RoomManager, Depends(get_room_manager)],
):
    password_hash = hash_password(body.password) if body.password is not None else None
    room = room_manager.create_room(body.host, password_hash)
    return RoomSummary.from_room(room)
