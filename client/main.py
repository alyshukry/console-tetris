import argparse
import curses
import os

from client.api import Api, ApiError
from client.endpoints import DEFAULT_SERVER, endpoints
from client.menu import auth_menu, main_menu
from client.session import play
from render.terminal import setup_curses
from render.widgets import busy, notice


def app(stdscr, server: str):
    http_base, ws_base = endpoints(server)
    setup_curses(stdscr)
    api = Api(http_base)
    while True:
        if api.access_token is None and not auth_menu(stdscr, api):
            return
        target = main_menu(stdscr, api)
        if target is None:
            if api.access_token is None:
                continue  # session expired -> back to login
            return
        busy(stdscr, "Joining room...")
        try:
            api.refresh()  # make sure the token is fresh at connect time
        except ApiError as e:
            notice(stdscr, e.detail)
            continue
        token = api.access_token
        if token is None:
            continue
        error = play(stdscr, ws_base, token, target)
        if error:
            notice(stdscr, error)


def main(server: str):
    os.environ.setdefault("ESCDELAY", "25")  # makes Esc instant; must be set before curses starts
    try:
        curses.wrapper(app, server)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "server",
        nargs="?",
        default=DEFAULT_SERVER,
        help=f"Server address (default: {DEFAULT_SERVER}), e.g. localhost:8000",
    )
    main(parser.parse_args().server)