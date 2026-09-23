import asyncio
import curses
import websockets
import sys

from render.curses_render import setup_curses, render_loop
from client.state import ClientState
from client.network import receive_loop, gravity_loop
from client.input import input_loop

def main(stdscr):
    setup_curses(stdscr)
    state = ClientState()
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

    async def run_client():
        async with websockets.connect(f"ws://{host}:8888") as ws:
            await asyncio.gather(
                input_loop(ws, stdscr, state),
                receive_loop(ws, state),
                gravity_loop(state),
                render_loop(stdscr, state),
            )

    asyncio.run(run_client())

curses.wrapper(main)