import curses


PIECE_COLORS = {
    "I": 1,
    "J": 2,
    "O": 3,
    "T": 4,
    "S": 5,
    "Z": 6,
    "L": 7,
}

GAME_OVER_PAIR = 9
EMPTY_PAIR = 10
BORDER_PAIR = 11
GARBAGE_PAIR = 8


def setup_colors():
    curses.init_color(20, 0, 940, 940)      # I - cyan
    curses.init_color(21, 0, 0, 940)        # J - blue
    curses.init_color(22, 940, 630, 0)     # L - orange
    curses.init_color(23, 940, 940, 0)     # O - yellow
    curses.init_color(24, 0, 940, 0)       # S - green
    curses.init_color(25, 630, 0, 940)     # T - purple
    curses.init_color(26, 940, 0, 0)       # Z - red
    curses.init_color(28, 600, 600, 600)    # gray
    curses.init_color(29, 0, 0, 500)       # blue border

    curses.init_pair(1, 20, curses.COLOR_BLACK)  # I
    curses.init_pair(2, 21, curses.COLOR_BLACK)  # J
    curses.init_pair(3, 23, curses.COLOR_BLACK)  # O
    curses.init_pair(4, 25, curses.COLOR_BLACK)  # T
    curses.init_pair(5, 24, curses.COLOR_BLACK)  # S
    curses.init_pair(6, 26, curses.COLOR_BLACK)  # Z
    curses.init_pair(7, 22, curses.COLOR_BLACK)  # L
    curses.init_pair(GAME_OVER_PAIR, 28, curses.COLOR_BLACK)
    curses.init_pair(EMPTY_PAIR, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(BORDER_PAIR, 29, curses.COLOR_BLACK)
    curses.init_pair(GARBAGE_PAIR, curses.COLOR_WHITE, curses.COLOR_BLACK)