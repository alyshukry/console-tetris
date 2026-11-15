import curses

from render.colors import setup_colors


def setup_curses(stdscr):
    """One-time terminal setup. Call once at startup."""
    curses.curs_set(0)
    curses.start_color()
    stdscr.keypad(True)
    setup_colors()


def enter_menu_mode(stdscr):
    """Menus block on getch() until a key is pressed."""
    stdscr.timeout(-1)


def enter_game_mode(stdscr):
    """In-game getch() returns after 50ms so the loops keep running."""
    stdscr.timeout(50)


def addstr_safe(stdscr, row, col, text, attributes=0):
    screen_height, screen_width = stdscr.getmaxyx()

    if row < 0 or row >= screen_height:
        return

    if col < 0:
        text = text[-col:]
        col = 0

    if col >= screen_width or not text:
        return

    text = text[: screen_width - col]

    try:
        stdscr.addstr(
            row,
            col,
            text,
            attributes,
        )
    except curses.error:
        pass