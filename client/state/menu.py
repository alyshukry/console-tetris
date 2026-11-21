from dataclasses import dataclass

from client.menu.types import Menu


@dataclass
class MenuState:
    current_menu: str = "start"
    selected_index: int | None = 0
    editing: bool = False
    message: str = ""
    message_kind: str = "info"  # "info" | "error"
    target_host: str | None = None
    # redraw: Callable | None = None

    @property
    def menu(self) -> Menu:  # the current menu, replaces the repeated lookup
        from client.menu.definitions import MENUS
        return MENUS[self.current_menu]


def set_message(menu_state: MenuState, msg: str, msg_kind: str = "info"):
    menu_state.message, menu_state.message_kind = msg, msg_kind
