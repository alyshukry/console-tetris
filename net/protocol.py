import asyncio
import json
import logging
from typing import TYPE_CHECKING

from websockets import ConnectionClosed
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
    targets = [ws for ws in list(room.connections) if not exclude or ws not in exclude]
    results = await asyncio.gather(
        *(send_json(ws, msg_type, data) for ws in targets),
        return_exceptions=True,
    )
    for r in results:
        if isinstance(r, Exception) and not isinstance(r, ConnectionClosed):
            logging.error("Broadcast failed", exc_info=r)
