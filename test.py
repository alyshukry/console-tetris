import curses
import time
import random
from dataclasses import dataclass, field

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


@dataclass
class Board:
    x: int
    y: int
    piece: Piece
    cells: list[list[int | str]] = field(
        default_factory=lambda: [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
    )

    def get_cell(self, row, col) -> None | str:
        if 0 <= row < len(self.cells) and 0 <= col < len(self.cells[0]):
            return self.cells[row][col]
        return None

    def draw(self, stdscr):
        for row in range(BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                cell = self.get_cell(row, col)
                if cell not in (0, None):
                    stdscr.addstr(row, col * 2, "██", curses.color_pair(COLORS[cell]))

    def clear_lines(self) -> int:
        new_rows = [row for row in self.cells if not all(cell != 0 for cell in row)]
        lines_cleared = BOARD_HEIGHT - len(new_rows)
        for _ in range(lines_cleared):
            new_rows.insert(0, [0] * BOARD_WIDTH)

        self.cells[:] = new_rows
        return lines_cleared

    def draw_piece(self, stdscr, shape: str, row: int, col: int, rot: int):
        for dr, dc in SHAPES[shape][rot]:
            stdscr.addstr(
                row + dr + self.x,
                (col + dc + self.y) * 2,
                "██",
                curses.color_pair(COLORS[shape]),
            )

    def kill_piece(self):
        for dr, dc in SHAPES[self.piece.shape][self.piece.rot % 4]:
            if self.get_cell(dr + self.piece.row, dc + self.piece.col) is not None:
                self.cells[dr + self.piece.row][dc + self.piece.col] = self.piece.shape
        self.clear_lines()
        self.piece.shape = random.choice(list(SHAPES.keys()))
        self.piece.row = 0
        self.piece.col = 0
        self.piece.rot = 0

    def move_piece_down(self) -> bool:
        for dr, dc in SHAPES[self.piece.shape][self.piece.rot % 4]:
            cell = self.get_cell(self.piece.row + dr + 1, self.piece.col + dc)
            if cell != 0:
                self.kill_piece()
                return False
        self.piece.row += 1
        return True

    def move_piece_right(self) -> bool:
        for dr, dc in SHAPES[self.piece.shape][self.piece.rot % 4]:
            cell = self.get_cell(self.piece.row + dr, self.piece.col + dc + 1)
            if cell != 0:
                return False
        self.piece.col += 1
        return True

    def move_piece_left(self) -> bool:
        for dr, dc in SHAPES[self.piece.shape][self.piece.rot % 4]:
            cell = self.get_cell(self.piece.row + dr, self.piece.col + dc - 1)
            if cell != 0:
                return False
        self.piece.col -= 1
        return True

    def rotate_piece(self) -> bool:
        self.piece.rot += 1
        return True


@dataclass
class Piece:
    shape: str
    row: int
    col: int
    rot: int


def fill_rect(stdscr, y1, x1, y2, x2, color_pair):
    for y in range(y1, y2 + 1):
        width = x2 - x1 + 1
        stdscr.addstr(y, x1, "██" * width, curses.color_pair(color_pair))


def main(stdscr):
    curses.curs_set(0)
    curses.start_color()

    # Custom color slots (id, R, G, B) — scaled 0-1000
    curses.init_color(20, 0, 940, 940)  # I - cyan
    curses.init_color(21, 0, 0, 940)  # J - blue
    curses.init_color(22, 940, 630, 0)  # L - orange
    curses.init_color(23, 940, 940, 0)  # O - yellow
    curses.init_color(24, 0, 940, 0)  # S - green
    curses.init_color(25, 630, 0, 940)  # T - purple
    curses.init_color(26, 940, 0, 0)  # Z - red
    curses.init_color(27, 192, 302, 475)  # background

    curses.init_pair(1, 20, curses.COLOR_BLACK)  # I
    curses.init_pair(2, 21, curses.COLOR_BLACK)  # J
    curses.init_pair(3, 23, curses.COLOR_BLACK)  # O
    curses.init_pair(4, 25, curses.COLOR_BLACK)  # T
    curses.init_pair(5, 24, curses.COLOR_BLACK)  # S
    curses.init_pair(6, 26, curses.COLOR_BLACK)  # Z
    curses.init_pair(7, 22, curses.COLOR_BLACK)  # L
    curses.init_pair(8, 27, curses.COLOR_BLACK)  # background fill

    stdscr.nodelay(True)  # getch() returns immediately even with no input
    stdscr.timeout(50)  # or: wait up to 50ms, then return -1 if nothing pressed

    board = Board(0, 0, Piece(random.choice(list(SHAPES.keys())), 0, 0, 0))

    last_drop = time.time()
    drop_interval = 0.25

    while True:
        key = stdscr.getch()
        if key == ord("q"):
            break

        if key == ord("a"):
            board.move_piece_left()
        if key == ord("d"):
            board.move_piece_right()
        if key == ord("x"):
            board.rotate_piece()

        now = time.time()
        if now - last_drop >= drop_interval:
            board.move_piece_down()
            last_drop = now

        stdscr.clear()
        fill_rect(
            stdscr, 0, 0, BOARD_HEIGHT - 1, BOARD_WIDTH - 1, 8
        )  # uses color pair 1's background
        try:
            board.draw(stdscr)
            board.draw_piece(
                stdscr,
                board.piece.shape,
                board.piece.row,
                board.piece.col,
                board.piece.rot % 4,
            )
        except curses.error:
            stdscr.clear()
            stdscr.addstr(0, 0, "Please expand console window.")

        stdscr.refresh()


curses.wrapper(main)
