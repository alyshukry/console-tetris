import asyncio
from typing import cast

from client.config import HTTP_BASE
from client.menu.controller import set_menu
from client.menu.types import Button, MenuItem, TextField
from client.session import connect_to_room, run_room
from client.state.client import ClientState
from client.state.menu import set_message
from client.state.session import Session
from client.api import api
from net.protocol import encode


def go_to(menu_name: str):
    async def action(state: ClientState):
        await set_menu(state, menu_name)

    return action


async def login(state: ClientState, username, password) -> bool:
    menu_state = state.menu_state
    set_message(menu_state, "Contacting server... (may take a while if asleep)", "info")

    res = await api(
        state, "POST", "/auth/login", json={"username": username, "password": password}
    )
    if res is None:
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
    fields = cast(list[TextField], menu.fixed_items[:2])
    username, password = (field.value for field in fields)
    if await login(state, username, password):
        await set_menu(state, "main")


async def submit_register(state: ClientState):
    menu_state = state.menu_state
    menu = state.menu_state.menu
    fields = cast(list[TextField], menu.fixed_items[:3])
    username, password, confirm = (field.value for field in fields)
    if password != confirm:
        set_message(menu_state, "Passwords don't match", "error")
        return

    set_message(menu_state, "Contacting server... (may take a while if asleep)", "info")

    res = await api(
        state,
        "POST",
        "/auth/register",
        json={"username": username, "password": password},
    )
    if res is None:
        return False

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

    res = await api(
        state,
        "POST",
        "/rooms",
        auth=True,
        json={"password": password} if password else {},
    )
    if res is None:
        return False

    if not res.ok:
        set_message(
            menu_state, res.json().get("detail", "Room creation failed"), "error"
        )
        return

    state.room_task = asyncio.create_task(
        run_room(state, session.username, session.access_token, password)
    )


async def load_rooms(state: ClientState):
    set_message(state.menu_state, "Loading rooms...")
    rooms = []

    res = await api(state, "GET", "/rooms", auth=True)
    if res is None:
        return
    
    set_message(state.menu_state, "")
    rooms = res.json()

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
    password_field = cast(TextField, state.menu_state.menu.fixed_items[0])
    password = password_field.value

    state.room_task = asyncio.create_task(
        run_room(state, host, session.access_token, password)
    )


async def leave_room(state: ClientState):
    await state.require_player_state().ws.close()
    state.player_state = None


async def toggle_ready(state: ClientState):
    player_state = state.require_player_state()
    await player_state.ws.send(encode("unready" if player_state.ready else "ready"))
