from client.menu.actions import (
    create_room,
    go_to,
    load_rooms,
    quit_app,
    submit_login,
    submit_register,
    submit_room_password,
)
from client.menu.types import Button, Menu, Separator, TextField

MENUS = {
    "start": Menu(
        fixed_items=[
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
        fixed_items=[
            TextField("Username"),
            TextField("Password", hide_chars=True),
            Button("Sign In", submit_login),
            Button("Go Back", go_to("start")),
        ],
    ),
    "register": Menu(
        title="Register",
        fixed_items=[
            TextField("Username"),
            TextField("Password", hide_chars=True),
            TextField("Confirm", hide_chars=True),
            Button("Sign Up", submit_register),
            Button("Go Back", go_to("start")),
        ],
    ),
    "main": Menu(
        fixed_items=[
            Button("Join Room", go_to("rooms")),
            Button("Create Room", go_to("create_room")),
            Button("Quit", quit_app),
        ],
        show_logo=True,
    ),
    "create_room": Menu(
        title="Create Room",
        fixed_items=[
            TextField("Password (blank for none)", hide_chars=True),
            Button("Create Room", create_room),
            Button("Go Back", go_to("main")),
        ],
    ),
    "rooms": Menu(
        title="Join Room",
        fixed_items=[Button("Refresh", go_to("rooms")), Button("Go Back", go_to("main"))],
        on_enter=load_rooms,
    ),
    "room_password": Menu(
        title="Enter Room Password",
        fixed_items=[
            TextField("Password", hide_chars=True),
            Button("Join", submit_room_password),
            Button("Go Back", go_to("rooms")),
        ],
    ),
    "error": Menu(
        fixed_items=[Button("OK", go_to("main"))],
    ),
    "lobby": Menu(
        title="Lobby",
        fixed_items=[
            Button("Go Back", go_to("rooms")),
        ],
    ),
}
