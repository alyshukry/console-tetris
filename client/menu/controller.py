import curses

from client.menu.types import Button, TextField
from client.ui.menu import draw_menu


# def run_menu(stdscr, menu_state):
#     context = Context(menu_state, MENUS, stdscr)

#     while True:
#         stdscr.clear()
#         draw_menu(stdscr, context.menu, context.menu_state)
#         stdscr.refresh()

#         key = stdscr.getch()

#         if context.menu_state.editing:
#             handle_text_input(context.menu_state, context.menu, key)
#         else:
#             handle_menu_input(context, key)


def move(state, menu, step):
    n = len(menu.items)
    for _ in range(n):
        state.selected_index = (state.selected_index + step) % n
        if isinstance(menu.items[state.selected_index], (Button, TextField)):
            return