from client.menu.actions import (
    create_room,
    go_to,
    load_rooms,
    quit_app,
    submit_login,
    submit_register,
)
from client.menu.types import Button, Menu, TextField

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
            TextField("Password", hide_chars=True),
            Button("Sign In", submit_login),
            Button("Go Back", go_to("start")),
        ],
    ),
    "register": Menu(
        title="Register",
        buttons=[
            TextField("Username"),
            TextField("Password", hide_chars=True),
            TextField("Confirm", hide_chars=True),
            Button("Sign Up", submit_register),
            Button("Go Back", go_to("start")),
        ],
    ),
    "main": Menu(
        buttons=[
            Button("Join Room", go_to("rooms")),
            Button("Create Room", go_to("create_room")),
            Button("Quit", quit_app),
        ],
        show_logo=True,
    ),
    "create_room": Menu(
        title="Create Room",
        buttons=[
            TextField("Password (blank for none)", hide_chars=True),
            Button("Create Room", create_room),
            Button("Go Back", go_to("main")),
        ],
    ),
    "rooms": Menu(
        title="Join Room",
        buttons=[Button("Refresh", go_to("rooms")), Button("Go Back", go_to("main"))],
        on_enter=load_rooms,
    ),
    "room_password": Menu(
        title="Enter Room Password",
        buttons=[TextField("Password", hide_chars=True), Button("Go Back", go_to("rooms"))],
    ),
    "error": Menu(
        buttons=[Button("OK", go_to("main"))],
    ),

}
