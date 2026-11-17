import curses

from client.menu.controller import run_menu
from client.state.menu import create_menu_state
from client.state.session import SessionState
from client.ui.curses import setup_curses


def main(stdscr):
    setup_curses(stdscr)
    run_menu(stdscr, create_menu_state(stdscr), SessionState())


if __name__ == "__main__":
    curses.wrapper(main)
