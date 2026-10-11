import asyncio
import json
import logging
from typing import TYPE_CHECKING

from websockets import ConnectionClosed
from websockets.asyncio.client import ClientConnection
from websockets.asyncio.server import ServerConnection

if TYPE_CHECKING:
    from server.models.room import Room


async def send_json(
    ws: ServerConnection | ClientConnection, msg_type: str, data: dict | None = None
):
    payload = {"type": msg_type, **(data or {})}
    await ws.send(json.dumps(payload))
