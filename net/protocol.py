import json
from typing import TYPE_CHECKING

from websockets.asyncio.server import ServerConnection
from websockets.asyncio.client import ClientConnection

if TYPE_CHECKING:
    from server.match import Match


async def send_json(
    ws: ServerConnection | ClientConnection, msg_type: str, data: dict | None = None
):
    payload = {"type": msg_type, **(data or {})}
    await ws.send(json.dumps(payload))

async def broadcast_json(
    match: "Match", msg_type: str, data: dict | None = None, exclude: list[ServerConnection] | None = None
):
    connections = match.connections
    for ws in connections.keys():
        if not exclude or ws not in exclude:
            await send_json(ws, msg_type, data)