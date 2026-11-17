from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from client.state.menu import MenuState
from client.state.session import Session


@dataclass
class Separator:
    label: str = ""


@dataclass
class Button:
    label: str
    action: Callable[[Context], None]


@dataclass
class TextField:
    label: str
    value: str = ""
    max_len: int = 20
    hide_chars: bool = False


@dataclass
class Context:
    menu_state: MenuState
    menus: dict[str, Menu]
    stdscr: Any
    session: Session | None = None

    @property
    def menu(self) -> Menu:  # the current menu, replaces the repeated lookup
        return self.menus[self.menu_state.current_menu]

    def require_session(self) -> Session:
        if self.session is None:
            raise RuntimeError("Not logged in")
        return self.session


@dataclass
class Menu:
    buttons: list[Button | TextField | Separator]
    title: str | None = None
    hint: str = "↑/↓ move    Enter select"
    show_logo: bool = False
    on_enter: Callable[[Context], None] | None = None
