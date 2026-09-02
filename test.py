import curses
import time

SHAPES = {
    "I": [
        [(1, 0), (1, 1), (1, 2), (1, 3)],  # 0°
        [(0, 2), (1, 2), (2, 2), (3, 2)],  # R (90° CW)
        [(2, 0), (2, 1), (2, 2), (2, 3)],  # 180°
        [(0, 1), (1, 1), (2, 1), (3, 1)],  # L (270°)
    ],
    "O": [
        [(0, 0), (0, 1), (1, 0), (1, 1)],  # same at every rotation
    ]
    * 4,
    "T": [
        [(0, 1), (1, 0), (1, 1), (1, 2)],  # 0°
        [(0, 1), (1, 1), (1, 2), (2, 1)],  # R
        [(1, 0), (1, 1), (1, 2), (2, 1)],  # 180°
        [(0, 1), (1, 0), (1, 1), (2, 1)],  # L
    ],
    "S": [
        [(0, 1), (0, 2), (1, 0), (1, 1)],  # 0°
        [(0, 1), (1, 1), (1, 2), (2, 2)],  # R
        [(1, 1), (1, 2), (2, 0), (2, 1)],  # 180°
        [(0, 0), (1, 0), (1, 1), (2, 1)],  # L
    ],
    "Z": [
        [(0, 0), (0, 1), (1, 1), (1, 2)],  # 0°
        [(0, 2), (1, 1), (1, 2), (2, 1)],  # R
        [(1, 0), (1, 1), (2, 1), (2, 2)],  # 180°
        [(0, 1), (1, 0), (1, 1), (2, 0)],  # L
    ],
    "J": [
        [(0, 0), (1, 0), (1, 1), (1, 2)],  # 0°
        [(0, 1), (0, 2), (1, 1), (2, 1)],  # R
        [(1, 0), (1, 1), (1, 2), (2, 2)],  # 180°
        [(0, 1), (1, 1), (2, 0), (2, 1)],  # L
    ],
    "L": [
        [(0, 2), (1, 0), (1, 1), (1, 2)],  # 0°
        [(0, 1), (1, 1), (2, 1), (2, 2)],  # R
        [(1, 0), (1, 1), (1, 2), (2, 0)],  # 180°
        [(0, 0), (0, 1), (1, 1), (2, 1)],  # L
    ],
}

COLORS = {
    "O": 3,
    "I": 1,
    "T": 4,
    "S": 5,
    "Z": 6,
    "L": 7,
    "J": 2,
}

BOARD_HEIGHT = 20
BOARD_WIDTH = 10


def draw_piece(stdscr, shape, x, y, rot):
    for dx, dy in SHAPES[shape][rot]:
        stdscr.addstr(x + dx, (y + dy) * 2, "██", curses.color_pair(COLORS[shape]))
    stdscr.addstr(x, y * 2, "██", curses.color_pair(6))


def move_piece_down(piece: list) -> bool:
    max = 0
    for x, _ in SHAPES[piece[0]][piece[3]]:
        if x > max:
            max = x
    if max + piece[1] < BOARD_HEIGHT - 1: # if bottom of the piece is within board
        piece[1] += 1
        return True
    else:
        return False

def move_piece_right(piece: list) -> bool:
    max = 0
    for _, y in SHAPES[piece[0]][piece[3]]:
        if y > max:
            max = y
    if max + piece[2] < BOARD_WIDTH - 1: # if bottom of the piece is within board
        piece[2] += 1
        return True
    else:
        return False

def move_piece_left(piece: list) -> bool:
    min = BOARD_WIDTH
    for _, y in SHAPES[piece[0]][piece[3]]:
        if y < min:
            min = y
    if min + piece[2] > 0: # if bottom of the piece is within board
        piece[2] -= 1
        return True
    else:
        return False

def fill_rect(stdscr, y1, x1, y2, x2, color_pair):
    for y in range(y1, y2 + 1):
        width = x2 - x1 + 1
        stdscr.addstr(y, x1, "  " * width, curses.color_pair(color_pair))

def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # I
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)  # J
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # O
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # T
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)  # S
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)  # Z
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_WHITE)

    stdscr.nodelay(True)  # getch() returns immediately even with no input
    stdscr.timeout(50)  # or: wait up to 50ms, then return -1 if nothing pressed

    pieces = [["S", 0, 0, 0], ["L", 3, 5, 3], ["S", 6, 2, 3]]

    last_drop = time.time()
    drop_interval = 1.5

    while True:
        key = stdscr.getch()
        if key == ord("q"):
            break

        if key == ord("a"): move_piece_left(pieces[0])
        if key == ord("d"): move_piece_right(pieces[0])

        now = time.time()
        if now - last_drop >= drop_interval:
            move_piece_down(pieces[0])
            last_drop = now

        stdscr.clear()
        fill_rect(stdscr, 0, 0, BOARD_HEIGHT - 1, BOARD_WIDTH - 1, 8)  # uses color pair 1's background
        try:
            stdscr.addstr(39, 19, "", curses.color_pair(1))
            for shape, x, y, rot in pieces:
                draw_piece(stdscr, shape, x, y, rot)
        except curses.error:
            stdscr.clear()
            stdscr.addstr(0, 0, "Please expand console window.")

        stdscr.refresh()


curses.wrapper(main)
