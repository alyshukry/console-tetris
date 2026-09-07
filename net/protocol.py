import json

from websockets.asyncio.server import ServerConnection
from typing import Any

async def send_json(ws: ServerConnection, type: str, data: dict):
    payload = {
        "type": type,
        **data
        }
    await ws.send(json.dumps(payload))
