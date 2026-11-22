import argparse
import asyncio

from client.actions.rooms import toggle_ready
from client.actions.auth import login
from client.api import api
from client.connection import run_room
from client.menu.controller import set_menu
from client.menu.types import MenuName
from client.state.client import ClientState

DEV_PASSWORD = "password"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dev", metavar="USER", help="auto-login as USER")
    p.add_argument("--create", action="store_true", help="create a room after login")
    p.add_argument("--join", metavar="HOST", help="join HOST's room after login")
    p.add_argument("--ready", action="store_true", help="ready up automatically")
    return p.parse_args()


async def dev_autostart(
    state: ClientState, user: str, create: bool, join: str | None, ready: bool
):
    if not await login(state, user, DEV_PASSWORD):  # first run: account doesn't exist
        body = {"username": user, "password": DEV_PASSWORD}
        await api(state, "POST", "/auth/register", json=body)
        if not await login(state, user, DEV_PASSWORD):
            return

    token = state.require_session().access_token
    if create:
        if await api(state, "POST", "/rooms", auth=True, json={}) is None:
            return
        host = user
    elif join:
        await asyncio.sleep(2)  # give the host time to create the room
        host = join
    else:
        await set_menu(state, MenuName.MAIN)
        return

    state.room_task = asyncio.create_task(run_room(state, host, token, None))
    if ready:
        for _ in range(100):  # wait up to ~10s for the connection
            if state.player_state is not None:
                break
            await asyncio.sleep(0.1)
        else:
            return
        # the host readies last, so the countdown doesn't start before others join
        await asyncio.sleep(4 if create else 0.5)
        await toggle_ready(state)
