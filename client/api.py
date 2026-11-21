import asyncio

import requests

from client.config import HTTP_BASE
from client.state.menu import set_message


async def api(state, method, path, *, auth=False, error="Request failed", **kw):
    headers = (
        {"Authorization": f"Bearer {state.require_session().access_token}"}
        if auth
        else {}
    )
    try:
        res = await asyncio.to_thread(
            requests.request,
            method,
            f"{HTTP_BASE}{path}",
            headers=headers,
            timeout=30,
            **kw,
        )
    except requests.RequestException:
        set_message(state.menu_state, "Can't reach server", "error")
        return None
    if not res.ok:
        set_message(state.menu_state, res.json().get("detail", error), "error")
        return None
    return res
