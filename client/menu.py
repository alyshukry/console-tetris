from typing import NamedTuple

from client.api import Api, ApiError
from render.widgets import Field, busy, form, menu, notice


class Target(NamedTuple):
    host: str
    password: str | None


def _auth_form(stdscr, api: Api, register: bool) -> bool:
    label = "Register" if register else "Login"
    fields = [Field("Username", max_len=16), Field("Password", hidden=True, max_len=64)]
    if register:
        fields.append(Field("Confirm", hidden=True, max_len=64))

    def submit(values: list[str]) -> str | None:
        username, password = values[0].strip(), values[1]
        if not username or not password:
            return "Enter a username and password"
        if register and password != values[2]:
            return "Passwords don't match"
        try:
            (api.register if register else api.login)(username, password)
        except ApiError as e:
            return e.detail
        return None

    return form(stdscr, label, fields, label, submit)


def auth_menu(stdscr, api: Api) -> bool:
    """Returns True once logged in, False if the user quits."""
    selected = 0
    while True:
        selected = menu(
            stdscr, "", ["Login", "Register", "Quit"],
            selected=selected if selected is not None else 0, logo=True, cancellable=False,
        )  # fmt: skip
        if selected == 2:
            return False
        if _auth_form(stdscr, api, register=selected == 1):
            return True


def _ask_room_password(stdscr, button: str) -> str | None:
    """Returns the entered password ('' if left blank), or None if the user went back."""
    entered: list[str] = []

    def submit(values: list[str]) -> str | None:
        entered.append(values[0])
        return None

    ok = form(stdscr, "Room password", [Field("Password", hidden=True)], button, submit)
    return entered[0] if ok else None


def join_menu(stdscr, api: Api) -> Target | None:
    while True:
        busy(stdscr, "Loading rooms...")
        try:
            rooms = api.list_rooms()
        except ApiError as e:
            notice(stdscr, e.detail)
            return None

        labels = [
            f"{r['host']}  {r['player_count']} players  "
            f"{'locked' if r['has_password'] else 'open'}  [{r['state']}]"
            for r in rooms
        ]
        choice = menu(
            stdscr, "Rooms", [*labels, "Refresh", "Back"],
            message=None if rooms else "No rooms available", is_error=False,
        )  # fmt: skip
        if choice is None or choice == len(labels) + 1:
            return None
        if choice == len(labels):
            continue  # refresh

        room = rooms[choice]
        password = None
        if room["has_password"]:
            password = _ask_room_password(stdscr, "Join")
            if password is None:
                continue  # went back to the room list
        return Target(room["host"], password)


def _create_room(stdscr, api: Api) -> Target | None:
    created: list[Target] = []

    def submit(values: list[str]) -> str | None:
        password = values[0] or None
        try:
            api.create_room(password)
        except ApiError as e:
            return e.detail
        assert api.username is not None
        created.append(Target(api.username, password))
        return None

    ok = form(
        stdscr,
        "Create room",
        [Field("Password (optional)", hidden=True)],
        "Create",
        submit,
    )
    return created[0] if ok else None


def main_menu(stdscr, api: Api) -> Target | None:
    """Returns a room to play in, or None (quit / session expired)."""
    selected = 0
    while True:
        selected = menu(
            stdscr, f"Signed in as {api.username}", ["Create room", "Join room", "Quit"],
            selected=selected, logo=True, cancellable=False,
        )  # fmt: skip
        if selected == 0:
            if target := _create_room(stdscr, api):
                return target
            if api.access_token is None:
                return None  # session expired -> back to login
        elif selected == 1:
            if target := join_menu(stdscr, api):
                return target
            if api.access_token is None:
                return None
        else:
            return None
