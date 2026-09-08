import curses

from game.constants import SHAPES, COLORS


def fill_rect(stdscr, x1, y1, x2, y2, color_pair):
    width = y2 - y1 + 1
    block = "██" * width
    for row in range(x1, x2 + 1):
        stdscr.addstr(row, y1 * 2, block, curses.color_pair(color_pair))


def draw(board: dict, stdscr, x: int, y: int, show_next: bool) -> list[int]: # returns total height and width of render 
    fill_rect(
        stdscr,
        x,
        y,
        x + board["height"] - 1,
        y + board["width"] - 1,
        10,
    )
    draw_border(board, stdscr, x, y)

    if show_next:
        fill_rect(
            stdscr,
            x + 2,
            board["width"] + y - 1 + 3,
            x + 6,
            board["width"] + y - 1 + 8,
            10
        )
        draw_piece(
            board, stdscr, x, y, board["next_piece"], 4, board["width"] + 4, 0
        )
        stdscr.addstr(x + 1, (board["width"] + y) * 2 + 4, "NEXT PIECE:")

    if not board["game_over"]:
        draw_ghost(board, stdscr, x, y)

    p = board["piece"]
    draw_piece(board, stdscr, x, y, p["shape"], p["row"], p["col"], p["rot"])

    for row in range(board["height"]):
        for col in range(board["width"]):
            cell = board["cells"][row][col]
            if cell not in (0, None):
                stdscr.addstr(
                    row + x,
                    (col + y) * 2,
                    "██",
                    curses.color_pair(9 if board["game_over"] else COLORS[cell]),
                )
                
    return [board["height"] + 2, board["width"] + 2 + (7 if show_next else 0)]


def draw_piece(board: dict, stdscr, bx, by, shape, row, col, rot):
    for dr, dc in SHAPES[shape][rot]:
        if row + dr + bx > 0:  # prevent from rendering above board
            stdscr.addstr(
                row + dr + bx,
                (col + dc + by) * 2,
                "██",
                curses.color_pair(9 if board["game_over"] else COLORS[shape]),
            )


def draw_ghost(board: dict, stdscr, bx, by):
    ghost_row = board["ghost_row"]
    p = board["piece"]
    for dr, dc in SHAPES[p["shape"]][p["rot"]]:
        stdscr.addstr(
            ghost_row + dr + bx,
            (p["col"] + dc + by) * 2,
            "░░",
            curses.color_pair(COLORS[p["shape"]]),
        )


def draw_border(board: dict, stdscr, bx, by):
    top = bx - 1
    left = (by * 2) - 2
    bottom = bx + board["height"]
    right = (by + board["width"]) * 2

    stdscr.addstr(top, left, " ▄" + "▄" * (board["width"] * 2) + "▄ ", curses.color_pair(11))
    # stdscr.addstr(top, left + 2, " USRNM ")
    for row in range(board["height"]):
        stdscr.addstr(bx + row, left, " █", curses.color_pair(11))
        stdscr.addstr(bx + row, right, "█ ", curses.color_pair(11))
    stdscr.addstr(bottom, left, " ▀" + "▀" * (board["width"] * 2) + "▀ ", curses.color_pair(11))


def setup_curses(stdscr):
    curses.curs_set(0)
    curses.start_color()
    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    curses.init_color(20, 0, 940, 940)  # I - cyan
    curses.init_color(21, 0, 0, 940)  # J - blue
    curses.init_color(22, 940, 630, 0)  # L - orange
    curses.init_color(23, 940, 940, 0)  # O - yellow
    curses.init_color(24, 0, 940, 0)  # S - green
    curses.init_color(25, 630, 0, 940)  # T - purple
    curses.init_color(26, 940, 0, 0)  # Z - red
    curses.init_color(28, 600, 600, 600)  # gray
    curses.init_color(29, 0, 0, 500)  # blue border

    curses.init_pair(1, 20, curses.COLOR_BLACK)  # I
    curses.init_pair(2, 21, curses.COLOR_BLACK)  # J
    curses.init_pair(3, 23, curses.COLOR_BLACK)  # O
    curses.init_pair(4, 25, curses.COLOR_BLACK)  # T
    curses.init_pair(5, 24, curses.COLOR_BLACK)  # S
    curses.init_pair(6, 26, curses.COLOR_BLACK)  # Z
    curses.init_pair(7, 22, curses.COLOR_BLACK)  # L
    curses.init_pair(9, 28, curses.COLOR_BLACK)  # gray
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_BLACK)  # black
    curses.init_pair(11, 29, curses.COLOR_BLACK)  # blue border