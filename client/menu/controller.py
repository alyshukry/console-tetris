import curses

from client.menu.definitions import MENUS
from client.menu.types import Button, Context, TextField
from client.ui.menu import draw_menu


def run_menu(stdscr, menu_state):
    context = Context(menu_state, MENUS, stdscr)

    while True:
        draw_menu(stdscr, context.menu, context.menu_state)

        key = stdscr.getch()

        if context.menu_state.editing:
            handle_text_input(context.menu_state, context.menu, key)
        else:
            handle_menu_input(context, key)


def move(state, menu, step):
    n = len(menu.buttons)
    for _ in range(n):
        state.selected_index = (state.selected_index + step) % n
        if isinstance(menu.buttons[state.selected_index], (Button, TextField)):
            return


def handle_text_input(state, menu, key):
    button = menu.buttons[state.selected_index % len(menu.buttons)]
    menu.hint = "type    Enter finish    Esc cancel"
    if key in (curses.KEY_ENTER, 10, 13, 27):  # Enter or Esc
        if key in (curses.KEY_ENTER, 10, 13):
            state.selected_index = (state.selected_index + 1) % len(menu.buttons)
        next_button = menu.buttons[state.selected_index]
        state.editing = isinstance(next_button, TextField)
    elif key in (curses.KEY_BACKSPACE, 127, 8):
        button.value = button.value[:-1]
    elif 32 <= key <= 126 and len(button.value) < button.max_len:
        button.value += chr(key)


def handle_menu_input(context, key):
    menu_state = context.menu_state
    menu = context.menu
    button = menu.buttons[menu_state.selected_index % len(menu.buttons)]
    menu.hint = "↑/↓ move    Enter select"
    if key == curses.KEY_UP:
        move(menu_state, menu, -1)
    elif key == curses.KEY_DOWN:
        move(menu_state, menu, 1)
    elif key in (curses.KEY_ENTER, 10, 13):
        if isinstance(button, TextField):
            menu_state.editing = True
        else:
            button.action(context)
