from dataclasses import dataclass
from typing import Callable

from client.actions import go_to, quit_app, submit_login, submit_register


@dataclass
class Button:
    label: str
    action: Callable


@dataclass
class TextField:
    label: str
    value: str = ""
    max_len: int = 20


@dataclass
class Menu:
    buttons: list[Button | TextField]
    title: str | None = None
    hint: str = "↑/↓ move    Enter select"
    show_logo: bool = False


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


def set_message(state: MenuState, msg: str, msg_kind: str = "info"):
    state.message, state.message_kind = msg, msg_kind
    if state.redraw:
        state.redraw()


MENUS = {
    "start": Menu(
        buttons=[
            Button("Login", go_to("login")),
            Button(
                "Register",
                go_to("register"),
            ),
            Button("Quit", quit_app),
        ],
        show_logo=True,
    ),
    "login": Menu(
        title="Login",
        buttons=[
            TextField("Username"),
            TextField("Password"),
            Button("Sign In", submit_login),
            Button("Go Back", go_to("start")),
        ],
    ),
    "register": Menu(
        title="Register",
        buttons=[
            TextField("Username"),
            TextField("Password"),
            TextField("Confirm"),
            Button("Sign Up", submit_register),
            Button("Go Back", go_to("start")),
        ],
    ),
}
