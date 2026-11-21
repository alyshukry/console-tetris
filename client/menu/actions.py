import asyncio

import requests

from client.config import HTTP_BASE
from client.menu.controller import set_menu
from client.menu.types import Button, MenuItem, TextField
from client.session import connect_to_room
from client.state.client import ClientState
from client.state.menu import set_message
from client.state.session import Session
from net.protocol import encode


def go_to(menu_name: str):
    async def action(state: ClientState):
        await set_menu(state, menu_name)

    return action


async def login(state: ClientState, username, password) -> bool:
    menu_state = state.menu_state
    set_message(menu_state, "Contacting server... (may take a while if asleep)", "info")
    try:
        res = await asyncio.to_thread(
            requests.post,
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
    state.session = Session(
        username=username,
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
    )
    return True


async def submit_login(state: ClientState):
    menu = state.menu_state.menu
    fields: list[TextField] = menu.fixed_items[:2]
    username, password = (field.value for field in fields)
    if await login(state, username, password):
        await set_menu(state, "main")


async def submit_register(state: ClientState):
    menu_state = state.menu_state
    menu = state.menu_state.menu
    fields: list[TextField] = menu.fixed_items[:3]
    username, password, confirm = (field.value for field in fields)
    if password != confirm:
        set_message(menu_state, "Passwords don't match", "error")
        return

    set_message(menu_state, "Contacting server... (may take a while if asleep)", "info")
    try:
        res = await asyncio.to_thread(
            requests.post,
            f"{HTTP_BASE}/auth/register",
            json={"username": username, "password": password},
            timeout=30,
        )
    except requests.RequestException:
        set_message(menu_state, "Can't reach server", "error")
        return

    if not res.ok:
        set_message(
            menu_state, res.json().get("detail", "Registration failed"), "error"
        )
        return

    if await login(state, username, password):
        await set_menu(state, "main")


async def quit_app(state: ClientState):
    raise SystemExit


async def create_room(state: ClientState):
    menu_state = state.menu_state
    session = state.require_session()
    menu = state.menu_state.menu
    password = getattr(menu.fixed_items[0], "value", None) or None
    try:
        res = await asyncio.to_thread(
            requests.post,
            f"{HTTP_BASE}/rooms",
            json={"password": password} if password else {},
            headers={"Authorization": f"Bearer {session.access_token}"},
            timeout=30,
        )
    except requests.RequestException:
        set_message(menu_state, "Can't reach server", "error")
        return
    if not res.ok:
        set_message(
            menu_state, res.json().get("detail", "Room creation failed"), "error"
        )
        return

    state.room_task = asyncio.create_task(
        run_room(state, session.username, session.access_token, password)
    )


async def load_rooms(state: ClientState):
    session = state.require_session()
    set_message(state.menu_state, "Loading rooms...")
    rooms = []
    try:
        res = await asyncio.to_thread(
            requests.get,
            f"{HTTP_BASE}/rooms",
            headers={"Authorization": f"Bearer {session.access_token}"},
            timeout=30,
        )
        res.raise_for_status()
        rooms = res.json()
    except (requests.RequestException, ValueError):
        set_message(state.menu_state, "Couldn't load rooms", "error")
        rooms = []
    else:
        state.menu_state.message = ""

    room_items: list[MenuItem] = []
    for r in rooms:
        room_items.append(
            Button(
                f"{r['host']} - ({r['player_count']} inside)",
                await select_room(r["host"], r["has_password"]),
            )
        )

    state.menu_state.menu.dynamic_items = room_items
    if not room_items:
        set_message(state.menu_state, "No rooms found", "info")


async def select_room(host, has_password):
    async def action(state: ClientState):
        if has_password:
            state.menu_state.target_host = host
            await set_menu(state, "room_password")
        else:
            await join_room(host)(state)

    return action


def join_room(host):
    async def action(state: ClientState):
        session = state.require_session()
        state.room_task = asyncio.create_task(
            run_room(state, host, session.access_token)
        )

    return action


async def submit_room_password(state: ClientState):
    session = state.require_session()
    host = state.menu_state.target_host
    if host is None:
        set_message(state.menu_state, "No room selected", "error")
        return
    password_field: TextField = state.menu_state.menu.fixed_items[0]
    password = password_field.value

    state.room_task = asyncio.create_task(
        run_room(state, host, session.access_token, password)
    )


async def run_room(
    client_state: ClientState, host: str, token: str, password: str | None = None
):
    error = await connect_to_room(client_state, host, token, password)
    await set_menu(client_state, "main")
    if error:
        set_message(client_state.menu_state, error, "error")


async def leave_room(state: ClientState):
    player_state = state.require_player_state()
    await player_state.ws.close()
    player_state = None
    set_message(state.menu_state, "Disconnected from room")
    await set_menu(state, "main")


async def toggle_ready(state: ClientState):
    player_state = state.require_player_state()
    await player_state.ws.send(encode("unready" if player_state.ready else "ready"))
