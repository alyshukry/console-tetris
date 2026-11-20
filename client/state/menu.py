from collections.abc import Callable
from dataclasses import dataclass


from client.menu.types import Menu


@dataclass
class MenuState:
    current_menu: str = "start"
    selected_index: int = 0
    editing: bool = False
    message: str = ""
    message_kind: str = "info"  # "info" | "error"
    target_host: str | None = None
    # redraw: Callable | None = None

    @property
    def menu(self) -> Menu:  # the current menu, replaces the repeated lookup
        from client.menu.definitions import MENUS
        return MENUS[self.current_menu]


def set_message(state: MenuState, msg: str, msg_kind: str = "info"):
    state.message, state.message_kind = msg, msg_kind
#     if state.redraw:
#         state.redraw()


# def create_menu_state(stdscr):
#     from client.menu.definitions import MENUS
#     from client.ui.menu import draw_menu

#     menu_state = MenuState()
#     menu_state.redraw = lambda: draw_menu(
#         stdscr, menu_state
#     )
#     return menu_state
