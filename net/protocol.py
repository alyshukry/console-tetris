import json
from typing import TYPE_CHECKING

from websockets.asyncio.server import ServerConnection
from websockets.asyncio.client import ClientConnection

if TYPE_CHECKING:
    from server.match import Match


async def send_json(
    ws: ServerConnection | ClientConnection, type: str, data: dict | None = None
):
    payload = {"type": type, **(data or {})}
    await ws.send(json.dumps(payload))

async def broadcast_json(
    match: "Match", type: str, data: dict | None = None
):
    connections = match.connections
    for ws in connections.keys():
        await send_json(ws, type, data)