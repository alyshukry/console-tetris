import json

from websockets import ClientConnection

from client.handlers import HANDLERS
from client.state.client import ClientState


async def receive_loop(ws: ClientConnection, state: ClientState):
    async for msg in ws:
        try:
            data = json.loads(msg)
        except json.JSONDecodeError:
            continue

        message_type = data.get("type") if isinstance(data, dict) else None
        handler = HANDLERS.get(message_type) if isinstance(message_type, str) else None
        if handler:
            await handler(state, data)
