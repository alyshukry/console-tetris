import curses

from client.ui.colors import setup_colors


def center(stdscr, row: int, text: str, attr=0):
    h, w = stdscr.getmaxyx()
    col = (w - len(text)) // 2
    addstr_safe(stdscr, row, col, text, attr)


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
        stdscr.addstr(row, col, text, attributes)
    except curses.error:
        pass


def setup_curses(stdscr):
    curses.curs_set(0)
    curses.start_color()

    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    setup_colors()
