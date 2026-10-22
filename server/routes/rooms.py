from fastapi import APIRouter

from server.dependencies import RoomManagerDep
from server.schemas.rooms import CreateRoomRequest, RoomSummary

router = APIRouter()


@router.post("/rooms", status_code=201, response_model=RoomSummary)
async def create_room(
    body: CreateRoomRequest,
    room_manager: RoomManagerDep,
) -> RoomSummary:
    room = await room_manager.create_room(body.host, body.password)
    return RoomSummary.from_room(room)


@router.get("/rooms", response_model=list[RoomSummary])
def get_rooms(room_manager: RoomManagerDep) -> list[RoomSummary]:
    return [RoomSummary.from_room(room) for room in room_manager.list_rooms()]
