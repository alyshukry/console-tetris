import argparse
import asyncio
import curses
from urllib.parse import urlencode

import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatus

from client.api import Api, ApiError
from client.input import input_loop
from client.menu import Target, auth_menu, main_menu
from client.network import gravity_loop, ping_loop, receive_loop
from client.state.client import ClientState
from render.curses_render import render_loop, setup_curses


def play(stdscr, ip: str, token: str, target: Target) -> str | None:
    setup_curses(stdscr)
    state = ClientState()
    params = {"host": target.host}
    if target.password:
        params["password"] = target.password
    url = f"ws://{ip}/ws?{urlencode(params)}"
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
    except ConnectionClosed as e:
        return (e.rcvd.reason if e.rcvd and e.rcvd.reason else "Disconnected")
    except InvalidStatus:
        return "Server rejected the connection"
    except KeyboardInterrupt:
        pass
    return None


def main(ip: str):
    api = Api(ip)
    while True:
        if api.access_token is None and not auth_menu(api):
            return
        target = main_menu(api)
        if target is None:
            if api.access_token is None:
                continue  # session expired -> back to login
            return
        try:
            api.refresh()  # make sure the token is fresh at connect time
        except ApiError as e:
            print(e.detail)
            continue
        token = api.access_token
        if token is None:
            continue
        error = curses.wrapper(play, ip, token, target)
        if error:
            print(error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="Server address, e.g. 127.0.0.1:8000")
    main(parser.parse_args().ip)