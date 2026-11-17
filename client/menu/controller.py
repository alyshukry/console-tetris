import curses

from client.menu.definitions import MENUS
from client.menu.types import HINTS, Button, TextField
from client.ui.menu import draw_menu


def run_menu(stdscr, menu_state, session_state):
    while True:
        menu = MENUS[menu_state.current_menu]
        draw_menu(stdscr, menu, menu_state)

        key = stdscr.getch()

        if menu_state.editing:
            handle_text_input(menu_state, menu, key)
        else:
            handle_menu_input(stdscr, menu_state, menu, key, session_state)


def move(state, menu, step):
    n = len(menu.buttons)
    for _ in range(n):
        state.selected_index = (state.selected_index + step) % n
        if isinstance(menu.buttons[state.selected_index], (Button, TextField)):
            return


def handle_text_input(state, menu, key):
    button = menu.buttons[state.selected_index % len(menu.buttons)]
    menu.hint = HINTS["editing"]
    if key in (curses.KEY_ENTER, 10, 13, 27):  # Enter or Esc
        if key in (curses.KEY_ENTER, 10, 13):
            state.selected_index = (state.selected_index + 1) % len(menu.buttons)
        next_button = menu.buttons[state.selected_index]
        state.editing = isinstance(next_button, TextField)
    elif key in (curses.KEY_BACKSPACE, 127, 8):
        button.value = button.value[:-1]
    elif 32 <= key <= 126 and len(button.value) < button.max_len:
        button.value += chr(key)


def handle_menu_input(stdscr, menu_state, menu, key, session_state):
    button = menu.buttons[menu_state.selected_index % len(menu.buttons)]
    menu.hint = HINTS["default"]
    if key == curses.KEY_UP:
        move(menu_state, menu, -1)
    elif key == curses.KEY_DOWN:
        move(menu_state, menu, 1)
    elif key in (curses.KEY_ENTER, 10, 13):
        if isinstance(button, TextField):
            menu_state.editing = True
        else:
            button.action(menu_state, MENUS, stdscr, session_state)
