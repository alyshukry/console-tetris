from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class MenuState:
    current_menu: str = "start"
    selected_index: int = 0
    editing: bool = False
    message: str = ""
    message_kind: str = "info"  # "info" | "error"
    redraw: Callable | None = None


def set_message(state: MenuState, msg: str, msg_kind: str = "info"):
    state.message, state.message_kind = msg, msg_kind
    if state.redraw:
        state.redraw()


def create_menu_state(stdscr):
    from client.menu.definitions import MENUS
    from client.ui.menu import draw_menu

    menu_state = MenuState()
    menu_state.redraw = lambda: draw_menu(stdscr, MENUS[menu_state.current_menu], menu_state)
    return menu_state
