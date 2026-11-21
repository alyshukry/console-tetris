import asyncio
import curses

from client.loops.input import input_loop
from client.loops.render import render_loop
from client.state.client import ClientState
from client.state.menu import MenuState
from client.ui.curses import setup_curses


async def async_main(stdscr):
    client_state = ClientState(MenuState())
    tasks = [
        asyncio.create_task(render_loop(stdscr, client_state)),
        asyncio.create_task(input_loop(stdscr, client_state)),
    ]
    try:
        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for t in done:
            t.result()  # surface any exception
    finally:
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


def main(stdscr):
    setup_curses(stdscr)
    asyncio.run(async_main(stdscr))


if __name__ == "__main__":
    curses.wrapper(main)
