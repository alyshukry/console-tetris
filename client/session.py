import asyncio
from urllib.parse import urlencode

import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatus

from client.input import LeaveRoom, input_loop
from client.menu import Target
from client.network import gravity_loop, ping_loop, receive_loop
from client.state.client import ClientState
from render.curses_render import render_loop
from render.terminal import enter_game_mode


def play(stdscr, ws_base: str, token: str, target: Target) -> str | None:
    """Runs one room session. Returns an error message, or None if the player left."""
    enter_game_mode(stdscr)
    state = ClientState()
    params = {"host": target.host}
    if target.password:
        params["password"] = target.password
    url = f"{ws_base}/ws?{urlencode(params)}"
    headers = {"Authorization": f"Bearer {token}"}

    async def run_player():
        async with websockets.connect(url, additional_headers=headers) as ws:
            await asyncio.gather(
                ping_loop(ws, state),
                input_loop(ws, stdscr, state),
                receive_loop(ws, state),
                gravity_loop(state),
                render_loop(stdscr, state),
            )

    try:
        asyncio.run(run_player())
    except LeaveRoom:
        pass
    except ConnectionClosed as e:
        return e.rcvd.reason if e.rcvd and e.rcvd.reason else "Disconnected"
    except InvalidStatus:
        return "Server rejected the connection"
    except OSError:
        return "Can't reach the server"
    except KeyboardInterrupt:
        pass
    return None