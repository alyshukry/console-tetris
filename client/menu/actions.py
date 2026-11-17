import requests

from client.config import HTTP_BASE
from client.menu.types import Button, Separator, set_message
from client.session import connect_to_room


def go_to(menu_name: str):
    def action(menu_state, menus, stdscr, session_state):
        menu_state.selected_index = 0
        menu_state.editing = False
        menu_state.message = ""
        menu_state.current_menu = menu_name
        if menus[menu_name].on_enter:
            menus[menu_name].on_enter(menu_state, menus, stdscr, session_state)

    return action


def login(menu_state, session_state, username, password) -> bool:
    set_message(menu_state, "Contacting server... (may take a while if asleep)", "info")
    try:
        res = requests.post(
            f"{HTTP_BASE}/auth/login",
            json={"username": username, "password": password},
            timeout=30,
        )
        session_state.username = username
    except requests.RequestException:
        set_message(menu_state, "Can't reach server", "error")
        return False

    if not res.ok:
        set_message(menu_state, res.json().get("detail", "Login failed"), "error")
        return False

    data = res.json()
    session_state.access_token = data["access_token"]
    session_state.refresh_token = data["refresh_token"]
    return True


def submit_login(menu_state, menus, stdscr, session_state):
    menu = menus[menu_state.current_menu]
    username, password = (f.value for f in menu.buttons[:2])
    if login(menu_state, session_state, username, password):
        go_to("main")(menu_state, menus, stdscr, session_state)


def submit_register(menu_state, menus, stdscr, session_state):
    menu = menus[menu_state.current_menu]
    username, password, confirm = (f.value for f in menu.buttons[:3])
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

    if login(menu_state, session_state, username, password):
        go_to("main")(menu_state, menus, stdscr, session_state)


def quit_app(menu_state, menus, stdscr, session_state):
    raise SystemExit


def create_room(menu_state, menus, stdscr, session_state):
    menu = menus[menu_state.current_menu]
    password = menu.buttons[0].value or None
    try:
        res = requests.post(
            f"{HTTP_BASE}/rooms",
            json={"password": password} if password else {},
            headers={"Authorization": f"Bearer {session_state.access_token}"},
            timeout=30,
        )
    except requests.RequestException:
        set_message(menu_state, "Can't reach server", "error")
        return
    if not res.ok:
        set_message(menu_state, res.json().get("detail", "Room creation failed"), "error")
        return

    error = connect_to_room(
        stdscr, session_state.username, session_state.access_token, password
    )

    go_to("main")(menu_state, menus, stdscr, session_state)
    if error:
        set_message(menu_state, error, "error")


def load_rooms(menu_state, menus, stdscr, session_state):
    menu = menus[menu_state.current_menu]
    set_message(menu_state, "Loading rooms...")
    rooms = []
    try:
        res = requests.get(
            f"{HTTP_BASE}/rooms",
            headers={"Authorization": f"Bearer {session_state.access_token}"},
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
    def action(menu_state, menus, stdscr, session_state):
        if has_password:
            # rebuild the password menu so its Join button remembers this host
            menus["room_password"].buttons[1] = Button(
                "Join", submit_room_password(host)
            )
            go_to("room_password")(menu_state, menus, stdscr, session_state)
        else:
            join_room(host)(menu_state, menus, stdscr, session_state)

    return action


def join_room(host):
    def action(menu_state, menus, stdscr, session_state):
        error = connect_to_room(stdscr, host, session_state.access_token)

        go_to("error")(menu_state, menus, stdscr, session_state)
        if error:
            set_message(menu_state, error, "error")

    return action


def submit_room_password(host):
    def action(menu_state, menus, stdscr, session_state):
        menu = menus[menu_state.current_menu]
        password = menu.buttons[0].value
        error = connect_to_room(stdscr, host, session_state.access_token, password)

        go_to("error")(menu_state, menus, stdscr, session_state)
        if error:
            set_message(menu_state, error, "error")

    return action
