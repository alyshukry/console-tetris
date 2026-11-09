from fastapi import APIRouter

from server.dependencies import RoomManagerDep
from server.schemas.rooms import RoomCreate, RoomResponse

router = APIRouter(tags=["Rooms"])


@router.post("/rooms", status_code=201, response_model=RoomResponse)
async def create_room(
    body: RoomCreate,
    room_manager: RoomManagerDep,
):
    room = await room_manager.create_room(body.host, body.password)
    return RoomResponse.from_room(room)


@router.get("/rooms", response_model=list[RoomResponse])
def get_rooms(room_manager: RoomManagerDep):
    return [RoomResponse.from_room(room) for room in room_manager.list_rooms()]
