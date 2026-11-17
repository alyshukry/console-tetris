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