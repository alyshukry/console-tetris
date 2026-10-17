
from pydantic import BaseModel

from server.types import Username


class CreateRoomRequest(BaseModel):
    host: Username
    password: str | None = None
