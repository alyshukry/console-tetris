import asyncio

import websockets
from websockets import ConnectionClosed, InvalidStatus

from client.config import WS_BASE
from client.input import input_loop
from client.network import gravity_loop, ping_loop, receive_loop
from client.state.client import ClientState, Screen
from client.state.game import PlayerState
from client.ui.game import render_loop


async def connect_to_room(
    client_state: ClientState, host: str, token: str, password: str | None = None
) -> str | None:

    params = f"?host={host}{'&password=' + password if password is not None else ''}"

    try:
        async with websockets.connect(
            f"{WS_BASE}/ws{params}",
            additional_headers={"Authorization": f"Bearer {token}"},
        ) as ws:
            client_state.screen = Screen.ROOM
            player_state = client_state.require_player_state()
            player_state.ws = ws
            tasks = [
                asyncio.create_task(c)
                for c in (
                    ping_loop(ws, player_state),
                    receive_loop(ws, player_state),
                    gravity_loop(player_state),
                )
            ]
            try:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for t in done:
                    t.result()
            finally:
                for t in tasks:
                    t.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
    except ConnectionClosed as e:
        return e.rcvd.reason if e.rcvd and e.rcvd.reason else "Disconnected"
    except InvalidStatus:
        return "Server rejected the connection"
    except OSError:
        return "Can't reach the server"
    except KeyboardInterrupt:
        pass
    return None
