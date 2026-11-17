import requests

from client.config import HTTP_BASE
from client.menu.types import Button, Context, Separator
from client.session import connect_to_room
from client.state.menu import set_message
from client.state.session import Session


def go_to(menu_name: str):
    def action(context: Context):
        menu_state = context.menu_state
        menu_state.selected_index = 0
        menu_state.editing = False
        menu_state.message = ""
        menu_state.current_menu = menu_name
        if context.menu.on_enter:
            context.menu.on_enter(context)

    return action


def login(context: Context, username, password) -> bool:
    menu_state = context.menu_state
    set_message(menu_state, "Contacting server... (may take a while if asleep)", "info")
    try:
        res = requests.post(
            f"{HTTP_BASE}/auth/login",
            json={"username": username, "password": password},
            timeout=30,
        )
    except requests.RequestException:
        set_message(menu_state, "Can't reach server", "error")
        return False

    if not res.ok:
        set_message(menu_state, res.json().get("detail", "Login failed"), "error")
        return False

    data = res.json()
    context.session = Session(
        username=username,
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
    )
    return True


def submit_login(context: Context):
    menu = context.menu
    username, password = (getattr(field, "value") for field in menu.buttons[:2])
    if login(context, username, password):
        go_to("main")(context)


def submit_register(context: Context):
    menu_state = context.menu_state
    menu = context.menu
    username, password, confirm = (getattr(field, "value") for field in menu.buttons[:3])
    if password != confirm:
        set_message(menu_state, "Passwords don't match", "error")
        return

    set_message(menu_state, "Contacting server... (may take a while if asleep)", "info")
    try:
        res = requests.post(
            f"{HTTP_BASE}/auth/register",
            json={"username": username, "password": password},
            timeout=30,
        )
    except requests.RequestException:
        set_message(menu_state, "Can't reach server", "error")
        return

    if not res.ok:
        set_message(menu_state, res.json().get("detail", "Registration failed"), "error")
        return

    if login(context, username, password):
        go_to("main")(context)


def quit_app(context: Context):
    raise SystemExit


def create_room(context: Context):
    menu_state = context.menu_state
    session = context.require_session()
    menu = context.menu
    password = getattr(menu.buttons[0], "value", None) or None
    try:
        res = requests.post(
            f"{HTTP_BASE}/rooms",
            json={"password": password} if password else {},
            headers={"Authorization": f"Bearer {session.access_token}"},
            timeout=30,
        )
    except requests.RequestException:
        set_message(menu_state, "Can't reach server", "error")
        return
    if not res.ok:
        set_message(menu_state, res.json().get("detail", "Room creation failed"), "error")
        return

    error = connect_to_room(
        context.stdscr, session.username, session.access_token, password
    )

    go_to("main")(context)
    if error:
        set_message(menu_state, error, "error")


def load_rooms(context: Context):
    menu_state = context.menu_state
    session = context.require_session()
    menu = context.menu
    set_message(menu_state, "Loading rooms...")
    rooms = []
    try:
        res = requests.get(
            f"{HTTP_BASE}/rooms",
            headers={"Authorization": f"Bearer {session.access_token}"},
            timeout=30,
        )
        res.raise_for_status()
        rooms = res.json()
    except (requests.RequestException, ValueError):
        set_message(menu_state, "Couldn't load rooms", "error")
        rooms = []
    else:
        menu_state.message = ""

    room_items = [
        Button(
            f"{r['host']} - ({r['player_count']} player{'s' if r['player_count'] != 1 else ''})",
            select_room(r["host"], r["has_password"]),
        )
        for r in rooms
    ] or [Separator("No Rooms Found")]

    menu.buttons = menu.buttons[-2:]
    menu.buttons = [*room_items, Separator(), *menu.buttons]


def select_room(host, has_password):
    def action(context: Context):
        if has_password:
            # rebuild the password menu so its Join button remembers this host
            context.menus["room_password"].buttons[1] = Button(
                "Join", submit_room_password(host)
            )
            go_to("room_password")(context)
        else:
            join_room(host)(context)

    return action


def join_room(host):
    def action(context: Context):
        session = context.require_session()
        error = connect_to_room(
            context.stdscr, host, session.access_token
        )

        go_to("error")(context)
        if error:
            set_message(context.menu_state, error, "error")

    return action


def submit_room_password(host):
    def action(context: Context):
        session = context.require_session()
        menu = context.menu
        password = getattr(menu.buttons[0], "value")
        error = connect_to_room(
            context.stdscr, host, session.access_token, password
        )

        go_to("error")(context)
        if error:
            set_message(context.menu_state, error, "error")

    return action
