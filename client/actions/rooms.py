import asyncio
from typing import cast

from client.api import api
from client.connection import run_room
from client.menu.controller import set_menu
from client.menu.types import Button, MenuItem, MenuName, TextField
from client.state.client import ClientState
from client.state.menu import set_message
from net.protocol import encode


async def create_room(state: ClientState):
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
            await set_menu(state, MenuName.ROOM_PASSWORD)
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
