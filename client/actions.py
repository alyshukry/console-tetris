import asyncio

import requests
import websockets
from websockets import ConnectionClosed, InvalidStatus

from client.input import input_loop
from client.network import gravity_loop, ping_loop, receive_loop
from client.state.game import PlayerState
from client.state.types import Button, Separator, set_message
from render.curses_render import render_loop


def go_to(menu_name: str):
    def action(state, menu, stdscr):
        from client.state.menu import MENUS  # avoid circular import

        state.selected_index = 0
        state.editing = False
        state.message = ""
        state.current_menu = menu_name
        target = MENUS[menu_name]
        if target.on_enter:
            target.on_enter(state, target, stdscr)

    return action


def login(state, username, password) -> bool:
    set_message(state, "Contacting server... (may take a while if asleep)", "info")
    try:
        res = requests.post(
            "https://console-tetris.onrender.com/auth/login",
            json={"username": username, "password": password},
            timeout=30,
        )
        state.username = username
    except requests.RequestException:
        set_message(state, "Can't reach server", "error")
        return False

    if not res.ok:
        set_message(state, res.json().get("detail", "Login failed"), "error")
        return False

    data = res.json()
    state.access_token = data["access_token"]
    state.refresh_token = data["refresh_token"]
    return True


def submit_login(state, menu, stdscr):
    username, password = (f.value for f in menu.buttons[:2])
    if login(state, username, password):
        go_to("main")(state, menu, stdscr)


def submit_register(state, menu, stdscr):
    username, password, confirm = (f.value for f in menu.buttons[:3])
    if password != confirm:
        set_message(state, "Passwords don't match", "error")
        return

    set_message(state, "Contacting server... (may take a while if asleep)", "info")
    try:
        res = requests.post(
            "https://console-tetris.onrender.com/auth/register",
            json={"username": username, "password": password},
            timeout=30,
        )
    except requests.RequestException:
        set_message(state, "Can't reach server", "error")
        return

    if not res.ok:
        set_message(state, res.json().get("detail", "Registration failed"), "error")
        return

    if login(state, username, password):
        go_to("main")(state, menu, stdscr)


def quit_app(state, menu, stdscr):
    raise SystemExit


def create_room(state, menu, stdscr):
    password = menu.buttons[0].value or None
    try:
        res = requests.post(
            "https://console-tetris.onrender.com/rooms",
            json={"password": password} if password else {},
            headers={"Authorization": f"Bearer {state.access_token}"},
            timeout=30,
        )
    except requests.RequestException:
        set_message(state, "Can't reach server", "error")
        return
    if not res.ok:
        set_message(state, res.json().get("detail", "Room creation failed"), "error")
        return

    error = connect_to_room(stdscr, state.username, state.access_token, password)

    go_to("main")(state, menu, stdscr)
    if error:
        set_message(state, error, "error")


def connect_to_room(
    stdscr, host: str, token: str, password: str | None = None
) -> str | None:

    player_state = PlayerState()

    async def ws_connect():
        async with websockets.connect(
            f"wss://console-tetris.onrender.com/ws?host={host}{'&password=' + password if password is not None else ''}",
            additional_headers={"Authorization": f"Bearer {token}"},
        ) as ws:
            await asyncio.gather(
                ping_loop(ws, player_state),
                input_loop(ws, stdscr, player_state),
                receive_loop(ws, player_state),
                gravity_loop(player_state),
                render_loop(stdscr, player_state),
            )

    try:
        asyncio.run(ws_connect())
    except ConnectionClosed as e:
        return e.rcvd.reason if e.rcvd and e.rcvd.reason else "Disconnected"
    except InvalidStatus:
        return "Server rejected the connection"
    except OSError:
        return "Can't reach the server"
    except KeyboardInterrupt:
        pass
    return None


def load_rooms(state, menu, stdscr):
    set_message(state, "Loading rooms...")
    rooms = []
    try:
        res = requests.get(
            "https://console-tetris.onrender.com/rooms",
            headers={"Authorization": f"Bearer {state.access_token}"},
            timeout=30,
        )
        res.raise_for_status()
        rooms = res.json()
    except (requests.RequestException, ValueError):
        set_message(state, "Couldn't load rooms", "error")
        rooms = []
    else:
        state.message = ""

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
    def action(state, menu, stdscr):
        from client.state.menu import MENUS

        if has_password:
            # rebuild the password menu so its Join button remembers this host
            MENUS["room_password"].buttons[1] = Button(
                "Join", submit_room_password(host)
            )
            go_to("room_password")(state, menu, stdscr)
        else:
            join_room(host)(state, menu, stdscr)

    return action


def join_room(host):
    def action(state, menu, stdscr):
        error = connect_to_room(stdscr, host, state.access_token)

        go_to("error")(state, menu, stdscr)
        if error:
            set_message(state, error, "error")

    return action


def submit_room_password(host):
    def action(state, menu, stdscr):
        password = menu.buttons[0].value
        error = connect_to_room(stdscr, host, state.access_token, password)

        go_to("error")(state, menu, stdscr)
        if error:
            set_message(state, error, "error")

    return action
