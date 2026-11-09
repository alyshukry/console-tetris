from pydantic import BaseModel

from server.models.room import Room
from shared.room_state import RoomState


class RoomCreate(BaseModel):
    password: str | None = None


class RoomResponse(BaseModel):
    host: str
    player_count: int
    has_password: bool
    state: RoomState

    @classmethod
    def from_room(cls, room: Room) -> "RoomResponse":
        return cls(
            host=room.host,
            player_count=len(room.connections),
            has_password=room.password_hash is not None,
            state=room.state,
        )
