from typing import cast

from client.api import api
from client.menu.controller import set_menu
from client.menu.types import MenuName, TextField
from client.state.client import ClientState
from client.state.menu import set_message
from client.state.session import Session


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
        await set_menu(state, MenuName.MAIN)


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
        return

    if not res.ok:
        set_message(
            menu_state, res.json().get("detail", "Registration failed"), "error"
        )
        return

    if await login(state, username, password):
        await set_menu(state, MenuName.MAIN)
