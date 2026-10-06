import asyncio
import curses
import sys

import websockets

from client.input import input_loop
from client.network import gravity_loop, ping_loop, receive_loop
from client.state.client import ClientState
from render.curses_render import render_loop, setup_curses


def main(stdscr):
    setup_curses(stdscr)
    state = ClientState()
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

    async def run_player():
        async with websockets.connect(f"ws://{host}:8888") as ws:
            await asyncio.gather(
                ping_loop(ws, state),
                input_loop(ws, stdscr, state),
                receive_loop(ws, state),
                gravity_loop(state),
                render_loop(stdscr, state),
            )

    asyncio.run(run_player())

curses.wrapper(main)
