import asyncio
import time

from websockets import ClientConnection

from client.state.game import PlayerState
from net.protocol import encode


async def ping_loop(ws: ClientConnection, player_state: PlayerState):
    while True:
        await ws.send(
            encode("ping", {"player_tick": player_state.tick, "sent_at": time.monotonic()})
        )
        await asyncio.sleep(1)
