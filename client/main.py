import asyncio
import curses

from client.dev import dev_autostart, parse_args
from client.loops.input import input_loop
from client.loops.render import render_loop
from client.state.client import ClientState
from client.state.menu import MenuState
from client.ui.curses import setup_curses


async def async_main(stdscr, args):
    state = ClientState(MenuState())
    tasks = [
        asyncio.create_task(render_loop(stdscr, state)),
        asyncio.create_task(input_loop(stdscr, state)),
    ]
    if args.dev:
        # deliberately not in `tasks`: it finishes on its own, which would end the app
        dev_task = asyncio.create_task(
            dev_autostart(state, args.dev, args.create, args.join, args.ready)
        )
    try:
        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for t in done:
            t.result()  # surface any exception
    finally:
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


def main(stdscr, args):
    setup_curses(stdscr)
    asyncio.run(async_main(stdscr, args))


if __name__ == "__main__":
    curses.wrapper(main, parse_args())
