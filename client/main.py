import asyncio
import curses
import websockets
import sys

from render.curses_render import setup_curses, render_loop
from client.state import PlayerState
from client.network import ping_loop, receive_loop, gravity_loop
from client.input import input_loop

def main(stdscr):
    setup_curses(stdscr)
    state = PlayerState()
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