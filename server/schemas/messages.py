from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter

from shared.action import Action


class InputMsg(BaseModel):
    type: Literal["input"]
    action: Action
    tick: int = Field(ge=0)
    seq: int = Field(ge=0)


class ReadyMsg(BaseModel):
    type: Literal["ready"]


class UnreadyMsg(BaseModel):
    type: Literal["unready"]


class PingMsg(BaseModel):
    type: Literal["ping"]
    sent_at: float


ClientMessage = Annotated[
    InputMsg | ReadyMsg | UnreadyMsg | PingMsg,
    Field(discriminator="type"),
]

_adapter = TypeAdapter(ClientMessage)


def parse_client_message(raw: str | bytes) -> ClientMessage:
    return _adapter.validate_json(raw)
