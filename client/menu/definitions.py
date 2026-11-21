from client.actions.auth import (
    submit_login,
    submit_register,
)
from client.actions.navigation import (
    go_to,
    quit_app,
)
from client.actions.rooms import (
    create_room,
    leave_room,
    load_rooms,
    submit_room_password,
    toggle_ready,
)
from client.menu.types import Button, Menu, MenuName, Separator, TextField


def back_to(menu: MenuName) -> Button:
    return Button("Go Back", go_to(menu))


MENUS: dict[MenuName, Menu] = {
    MenuName.START: Menu(
        fixed_items=[
            Button("Login", go_to(MenuName.LOGIN)),
            Button(
                "Register",
                go_to(MenuName.REGISTER),
            ),
            Button("Quit", quit_app),
        ],
        show_logo=True,
    ),
    MenuName.LOGIN: Menu(
        title="Login",
        fixed_items=[
            TextField("Username"),
            TextField("Password", hide_chars=True),
            Button("Sign In", submit_login),
            back_to(MenuName.START),
        ],
    ),
    MenuName.REGISTER: Menu(
        title="Register",
        fixed_items=[
            TextField("Username"),
            TextField("Password", hide_chars=True),
            TextField("Confirm", hide_chars=True),
            Button("Sign Up", submit_register),
            back_to(MenuName.START),
        ],
    ),
    MenuName.MAIN: Menu(
        fixed_items=[
            Button("Join Room", go_to(MenuName.ROOMS)),
            Button("Create Room", go_to(MenuName.CREATE_ROOM)),
            Button("Quit", quit_app),
        ],
        show_logo=True,
    ),
    MenuName.CREATE_ROOM: Menu(
        title="Create Room",
        fixed_items=[
            TextField("Password (blank for none)", hide_chars=True),
            Button("Create Room", create_room),
            back_to(MenuName.MAIN),
        ],
    ),
    MenuName.ROOMS: Menu(
        title="Join Room",
        fixed_items=[
            Button("Refresh", go_to(MenuName.ROOMS)),
            back_to(MenuName.MAIN),
        ],
        on_enter=load_rooms,
    ),
    MenuName.ROOM_PASSWORD: Menu(
        title="Enter Room Password",
        fixed_items=[
            TextField("Password", hide_chars=True),
            Button("Join", submit_room_password),
            back_to(MenuName.ROOMS),
        ],
    ),
    MenuName.LOBBY: Menu(
        title="Lobby",
        fixed_items=[
            Separator(
                lambda state: (
                    f"{getattr(state.player_state, 'ready_count', 0)}/"
                    f"{getattr(state.player_state, 'player_count', 0)} players ready"
                )
            ),
            Separator(),
            Button(
                lambda state: (
                    "Unready"
                    if getattr(state.player_state, "ready", False)
                    else "Ready"
                ),
                toggle_ready,
            ),
            Button("Leave Room", leave_room),
        ],
    ),
    MenuName.COUNTDOWN: Menu(
        fixed_items=[
            Separator(
                lambda s: (
                    f"Starting in {(c := getattr(s.player_state, 'countdown', 0))} seconds"
                    f"{'.' * (c % 3 + 1)}"
                )
            ),
        ],
        hint="",
    ),
    MenuName.RESULTS: Menu(
        fixed_items=[
            Separator(
                lambda s: (
                    f"{(w := getattr(s.player_state, 'winners', []))} "
                    f"win{'s' if len(w) == 1 else ''} the game!"
                )
            ),
        ],
        hint="",
    ),
}
