import asyncio

import websockets
from websockets import ConnectionClosed, InvalidStatus

from client.config import WS_BASE
from client.loops.gravity import gravity_loop
from client.loops.ping import ping_loop
from client.loops.receive import receive_loop
from client.menu.controller import set_menu
from client.menu.types import MenuName
from client.state.client import ClientState
from client.state.game import PlayerState
from client.state.menu import set_message


async def connect_to_room(
    state: ClientState, host: str, token: str, password: str | None = None
) -> str | None:

    params = f"?host={host}{'&password=' + password if password is not None else ''}"

    try:
        async with websockets.connect(
            f"{WS_BASE}/ws{params}",
            additional_headers={"Authorization": f"Bearer {token}"},
        ) as ws:
            player_state = PlayerState(ws)
            state.player_state = player_state
            await set_menu(state, MenuName.LOBBY)
            tasks = [
                asyncio.create_task(c)
                for c in (
                    ping_loop(ws, player_state),
                    receive_loop(ws, state),
                    gravity_loop(player_state),
                )
            ]
            try:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for t in done:
                    t.result()
            finally:
                state.player_state = None
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


async def run_room(
    state: ClientState, host: str, token: str, password: str | None = None
):
    error = await connect_to_room(state, host, token, password)
    await set_menu(state, MenuName.MAIN)
    if error:
        set_message(state.menu_state, error, "error")
