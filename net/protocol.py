import json

from websockets.asyncio.server import ServerConnection
from websockets.asyncio.client import ClientConnection


async def send_json(
    ws: ServerConnection | ClientConnection, type: str, data: dict | None = None
):
    payload = {"type": type, **(data or {})}
    await ws.send(json.dumps(payload))
