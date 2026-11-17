from client.menu.definitions import MENUS
from client.menu.types import MenuState
from client.ui.menu import draw_menu


def create_menu_state(stdscr):
    menu_state = MenuState()
    menu_state.redraw = lambda: draw_menu(stdscr, MENUS[menu_state.current_menu], menu_state)
    return menu_state
