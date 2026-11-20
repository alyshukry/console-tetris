from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Awaitable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.state.client import ClientState

type Action = Callable[[ClientState], Awaitable[None]]


@dataclass
class Separator:
    label: str = ""


@dataclass
class Button:
    label: str
    action: Action


@dataclass
class TextField:
    label: str
    value: str = ""
    max_len: int = 20
    hide_chars: bool = False


type MenuItem = Button | Separator | TextField


@dataclass
class Menu:
    fixed_items: list[MenuItem]
    dynamic_items: list[MenuItem] = field(default_factory=list)
    title: str | None = None
    hint: str = "↑/↓ move    Enter select"
    show_logo: bool = False
    on_enter: Action | None = None

    @property
    def items(self) -> list[MenuItem]:
        sep = [Separator()] if self.dynamic_items else []
        return [*self.dynamic_items, *sep, *self.fixed_items]
