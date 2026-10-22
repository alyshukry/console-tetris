from pydantic import BaseModel

from server.schemas.common import Username
from shared.room_state import RoomState
from server.models.room import Room


class CreateRoomRequest(BaseModel):
    host: Username
    password: str | None = None


class RoomSummary(BaseModel):
    host: str
    player_count: int
    has_password: bool
    state: RoomState

    @classmethod
    def from_room(cls, room: Room) -> "RoomSummary":
        return cls(
            host=room.host,
            player_count=len(room.connections),
            has_password=room.password_hash is not None,
            state=room.state,
        )
