import json
from typing import TYPE_CHECKING

from websockets.asyncio.client import ClientConnection
from websockets.asyncio.server import ServerConnection

if TYPE_CHECKING:
    pass


async def send_json(
    ws: ServerConnection | ClientConnection, msg_type: str, data: dict | None = None
):
    payload = {"type": msg_type, **(data or {})}
    await ws.send(json.dumps(payload))
