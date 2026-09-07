import json

from websockets.asyncio.server import ServerConnection
from websockets.asyncio.client import ClientConnection
from typing import Any

async def send_json(ws: ServerConnection | ClientConnection, type: str, data: dict):
    payload = {
        "type": type,
        **data
        }
    await ws.send(json.dumps(payload))
