import asyncio

import websockets
from websockets import ConnectionClosed, InvalidStatus

from client.config import WS_BASE
from client.input import input_loop
from client.network import gravity_loop, ping_loop, receive_loop
from client.state.game import PlayerState
from client.ui.game import render_loop


def connect_to_room(
    stdscr, host: str, token: str, password: str | None = None
) -> str | None:

    player_state = PlayerState()
    params = f"?host={host}{'&password=' + password if password is not None else ''}"

    async def ws_connect():
        async with websockets.connect(
            f"{WS_BASE}/ws{params}",
            additional_headers={"Authorization": f"Bearer {token}"},
        ) as ws:
            tasks = [
                asyncio.create_task(c)
                for c in (
                    ping_loop(ws, player_state),
                    input_loop(ws, stdscr, player_state),
                    receive_loop(ws, player_state),
                    gravity_loop(player_state),
                    render_loop(stdscr, player_state),
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

    try:
        asyncio.run(ws_connect())
    except ConnectionClosed as e:
        return e.rcvd.reason if e.rcvd and e.rcvd.reason else "Disconnected"
    except InvalidStatus:
        return "Server rejected the connection"
    except OSError:
        return "Can't reach the server"
    except KeyboardInterrupt:
        pass
    return None
