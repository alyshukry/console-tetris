from getpass import getpass
from typing import NamedTuple

from client.api import Api, ApiError


class Target(NamedTuple):
    host: str
    password: str | None


def menu(title: str, options: list[str]) -> int:
    print(f"\n== {title} ==")
    for i, opt in enumerate(options, 1):
        print(f"{i}) {opt}")
    while True:
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        print("Invalid choice")


def auth_menu(api: Api) -> bool:
    """Returns True once logged in, False if the user quits."""
    while True:
        choice = menu("Tetris Battle", ["Login", "Register", "Quit"])
        if choice == 3:
            return False
        username = input("Username: ").strip()
        password = getpass("Password: ")
        try:
            (api.login if choice == 1 else api.register)(username, password)
            return True
        except ApiError as e:
            print(e.detail)


def join_menu(api: Api) -> Target | None:
    try:
        rooms = api.list_rooms()
    except ApiError as e:
        print(e.detail)
        return None
    if not rooms:
        print("No rooms available")
        return None
    labels = [
        f"{r['host']}  {r['player_count']} players  "
        f"{'locked' if r['has_password'] else 'open'}  [{r['state']}]"
        for r in rooms
    ]
    choice = menu("Rooms", [*labels, "Back"])
    if choice == len(labels) + 1:
        return None
    room = rooms[choice - 1]
    password = getpass("Room password: ") if room["has_password"] else None
    return Target(room["host"], password)


def main_menu(api: Api) -> Target | None:
    """Returns a room to play in, or None (quit / session expired)."""
    while True:
        match menu("Main menu", ["Create room", "Join room", "Quit"]):
            case 1:
                password = getpass("Room password (blank for none): ") or None
                try:
                    api.create_room(password)
                except ApiError as e:
                    print(e.detail)
                    if api.access_token is None:
                        return None
                    continue
                assert api.username is not None
                return Target(api.username, password)
            case 2:
                if target := join_menu(api):
                    return target
            case 3:
                return None