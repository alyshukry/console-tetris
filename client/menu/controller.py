import curses

from client.menu.types import Button, TextField
from client.ui.menu import draw_menu


async def set_menu(state, menu_name):
    menu_state = state.menu_state
    menu_state.selected_index = 0
    menu_state.editing = False
    menu_state.message = ""
    menu_state.current_menu = menu_name
    if menu_state.menu.on_enter:
        await menu_state.menu.on_enter(state)

def move(state, menu, step):
    n = len(menu.items)
    for _ in range(n):
        state.selected_index = (state.selected_index + step) % n
        if isinstance(menu.items[state.selected_index], (Button, TextField)):
            return