import json
from typing import TYPE_CHECKING

from websockets.asyncio.client import ClientConnection
from websockets.asyncio.server import ServerConnection

if TYPE_CHECKING:
    from server.room import Room


async def send_json(
    ws: ServerConnection | ClientConnection, msg_type: str, data: dict | None = None
):
    payload = {"type": msg_type, **(data or {})}
    await ws.send(json.dumps(payload))


async def broadcast_json(
    room: "Room",
    msg_type: str,
    data: dict | None = None,
    exclude: list[ServerConnection] | None = None,
):
    for ws in list(room.connections):
        if not exclude or ws not in exclude:
            await send_json(ws, msg_type, data)
