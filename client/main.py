import asyncio
import curses
from typing import Callable

import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatus

from client.input import input_loop
from client.network import gravity_loop, ping_loop, receive_loop
from client.state.game import PlayerState
from client.state.menu import MENUS, MenuState, TextField
from render.curses_render import render_loop, setup_curses
from render.menu import draw_menu


def connect_to_room(
    stdscr, host: str, token: str, password: str | None = None
) -> str | None:

    player_state = PlayerState()

    async def ws_connect():
        async with websockets.connect(
            f"wss://console-tetris.onrender.com/ws?host={host}{"?password=" + password if password is not None else ""}",
            additional_headers={"Authorization": f"Bearer {token}"},
        ) as ws:
            await asyncio.gather(
                ping_loop(ws, player_state),
                input_loop(ws, stdscr, player_state),
                receive_loop(ws, player_state),
                gravity_loop(player_state),
                render_loop(stdscr, player_state),
            )

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


def main(stdscr):
    setup_curses(stdscr)
    menu_state = MenuState()
    menu_state.redraw = lambda: draw_menu(stdscr, menu_state)
    while True:
        draw_menu(stdscr, menu_state)

        menu = MENUS[menu_state.current_menu]
        item = menu.buttons[menu_state.selected_index % len(menu.buttons)]
        key = stdscr.getch()

        if menu_state.editing:
            assert isinstance(item, TextField)
            if key in (curses.KEY_ENTER, 10, 13, 27):  # Enter or Esc
                if key in (curses.KEY_ENTER, 10, 13):
                    menu_state.selected_index = (menu_state.selected_index + 1) % len(
                        menu.buttons
                    )
                next_item = menu.buttons[menu_state.selected_index]
                menu_state.editing = isinstance(next_item, TextField)
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                item.value = item.value[:-1]
            elif 32 <= key <= 126 and len(item.value) < item.max_len:
                item.value += chr(key)
        else:
            if key == curses.KEY_UP:
                menu_state.selected_index = (menu_state.selected_index - 1) % len(
                    menu.buttons
                )
            elif key == curses.KEY_DOWN:
                menu_state.selected_index = (menu_state.selected_index + 1) % len(
                    menu.buttons
                )
            elif key in (curses.KEY_ENTER, 10, 13):
                menu_state.selected_index = 0
                menu_state.editing = False
                menu_state.message = ""
                if isinstance(item, TextField):
                    menu_state.editing = True
                else:
                    item.action(menu_state, menu)


curses.wrapper(main)
