import argparse
import asyncio
import curses
from urllib.parse import urlencode

import websockets

from client.input import input_loop
from client.network import gravity_loop, ping_loop, receive_loop
from client.state.client import ClientState
from render.curses_render import render_loop, setup_curses


def main(stdscr, ip, host, password):
    setup_curses(stdscr)
    state = ClientState()
    query = urlencode({"host": host, "password": password})

    async def run_player():
        async with websockets.connect(f"ws://{ip}:8888/ws?{query}") as ws:
            await asyncio.gather(
                ping_loop(ws, state),
                input_loop(ws, stdscr, state),
                receive_loop(ws, state),
                gravity_loop(state),
                render_loop(stdscr, state),
            )

    asyncio.run(run_player())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="Server IP address")
    parser.add_argument("host", help="Player username")
    parser.add_argument("password", help="Room password")
    args = parser.parse_args()
    curses.wrapper(main, args.ip, args.host, args.password)
