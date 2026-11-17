from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Separator:
    label: str = ""


@dataclass
class Button:
    label: str
    action: Callable


@dataclass
class TextField:
    label: str
    value: str = ""
    max_len: int = 20
    hide_chars: bool = False


HINTS = {
    "default": "↑/↓ move    Enter select",
    "editing": "type    Enter finish    Esc cancel",
}


@dataclass
class Menu:
    buttons: list[Button | TextField]
    title: str | None = None
    hint: str = HINTS["default"]
    show_logo: bool = False
    on_enter: Callable | None = None


@dataclass
class MenuState:
    current_menu: str = "start"
    selected_index: int = 0
    editing: bool = False
    message: str = ""
    message_kind: str = "info"  # "info" | "error"
    access_token: str | None = None
    refresh_token: str | None = None
    redraw: Callable | None = None
    username: str | None = None


def set_message(state: MenuState, msg: str, msg_kind: str = "info"):
    state.message, state.message_kind = msg, msg_kind
    if state.redraw:
        state.redraw()
