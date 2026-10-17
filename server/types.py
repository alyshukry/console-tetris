from typing import Annotated, TypeAlias

from pydantic import Field

from server.models.room import Room

Rooms: TypeAlias = dict[str, Room]
Username: TypeAlias = Annotated[str, Field(pattern=r"^[a-z0-9_]{3,16}$")]
