import curses

SHAPES = {
    "O": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "I": [(0, 0), (0, 1), (0, 2), (0, 3)],
    "T": [(0, 0), (0, 1), (0, 2), (1, 1)],
    "S": [(1, 0), (1, 1), (0, 1), (0, 2)],
    "Z": [(0, 0), (0, 1), (1, 1), (1, 2)],
    "L": [(0, 0), (1, 0), (2, 0), (2, 1)],
    "J": [(0, 1), (1, 1), (2, 1), (2, 0)],
}

COLORS = {
    "O": 3, "I": 1, "T": 4, "S": 5, "Z": 6, "L": 7, "J": 2,
}

def draw_piece(stdscr, shape, x, y):
    for dx, dy in SHAPES[shape]:
        stdscr.addstr(x + dx, (y + dy) * 2, "██", curses.color_pair(COLORS[shape]))

def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)     # I
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)     # J
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # O
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # T
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)    # S
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)      # Z
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)    # L (orange isn't a base curses color, white/yellow-ish is the common substitute)
    stdscr.nodelay(True)  # getch() returns immediately even with no input
    stdscr.timeout(50)   # or: wait up to 100ms, then return -1 if nothing pressed
    
    pieces = [("O", 1, 1), ("L", 3, 5), ("S", 6, 2)]
    
    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break

        stdscr.clear()
        try:
            stdscr.addstr(39, 19, "", curses.color_pair(1))
            for shape, x, y in pieces:
                draw_piece(stdscr, shape, x, y)
        except curses.error:
            stdscr.clear()
            stdscr.addstr(0, 0, "Please expand console window.")

        stdscr.refresh()

curses.wrapper(main)