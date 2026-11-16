import asyncio
import curses
from typing import Callable

import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatus

from client.input import input_loop
from client.network import gravity_loop, ping_loop, receive_loop
from client.state.game import PlayerState
from client.state.menu import MENUS
from client.state.types import Button, MenuState, TextField
from render.curses_render import render_loop, setup_curses
from render.menu import draw_menu


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
                move(menu_state, menu, -1)
            elif key == curses.KEY_DOWN:
                move(menu_state, menu, 1)
            elif key in (curses.KEY_ENTER, 10, 13):
                if isinstance(item, TextField):
                    menu_state.editing = True
                else:
                    item.action(menu_state, menu, stdscr)


def move(state, menu, step):
    n = len(menu.buttons)
    for _ in range(n):
        state.selected_index = (state.selected_index + step) % n
        if isinstance(menu.buttons[state.selected_index], (Button, TextField)):
            return


curses.wrapper(main)
