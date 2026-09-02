import curses
import time
import random
from dataclasses import dataclass, field

SHAPES = {
    "I": [
        [(-1, -2), (-1, -1), (-1, 0), (-1, 1)],  # 0°
        [(-2, 0), (-1, 0), (0, 0), (1, 0)],  # R (90° CW)
        [(0, -2), (0, -1), (0, 0), (0, 1)],  # 180°
        [(-2, -1), (-1, -1), (0, -1), (1, -1)],  # L (270°)
    ],
    "O": [
        [(0, 0), (0, -1), (-1, 0), (-1, -1)],  # same at every rotation
    ]
    * 4,
    "T": [
        [(0, 0), (0, 1), (0, -1), (-1, 0)],  # 0°
        [(0, 0), (0, 1), (1, 0), (-1, 0)],  # R
        [(0, 0), (1, 0), (0, 1), (0, -1)],  # 180°
        [(0, 0), (0, -1), (1, 0), (-1, 0)],  # L
    ],
    "S": [
        [(0, 0), (-1, 0), (-1, 1), (0, -1)],  # 0°
        [(0, 0), (0, 1), (-1, 0), (1, 1)],  # R
        [(0, 0), (0, 1), (1, -1), (1, 0)],  # 180°
        [(0, 0), (-1, -1), (1, 0), (0, -1)],  # L
    ],
    "Z": [
        [(0, 0), (-1, 0), (-1, -1), (0, 1)],  # 0°
        [(0, 0), (0, 1), (1, 0), (-1, 1)],  # R
        [(0, 0), (0, -1), (1, 1), (1, 0)],  # 180°
        [(0, 0), (1, -1), (-1, 0), (0, -1)],  # L
    ],
    "J": [
        [(0, 0), (0, 1), (0, -1), (-1, -1)],  # 0°
        [(0, 0), (1, 0), (-1, 0), (-1, 1)],  # R
        [(0, 0), (0, 1), (1, 1), (0, -1)],  # 180°
        [(0, 0), (1, 0), (-1, 0), (1, -1)],  # L
    ],
    "L": [
        [(0, 0), (0, -1), (0, 1), (-1, 1)],  # 0°
        [(0, 0), (-1, 0), (1, 0), (1, 1)],  # R
        [(0, 0), (0, -1), (1, -1), (0, 1)],  # 180°
        [(0, 0), (-1, 0), (1, 0), (-1, -1)],  # L
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


@dataclass
class Piece:
    shape: str
    row: int
    col: int
    rot: int


@dataclass
class Board:
    x: int
    y: int
    bag: SevenBag
    show_next: bool = True
    piece_index: int = 0
    height: int = 20
    width: int = 10
    cells: list[list[int | str]] = field(init=False)
    piece: Piece = field(init=False)

    def __post_init__(self):
        self.cells = [[0] * self.width for _ in range(self.height)]
        self.piece = Piece(self.bag.get(0), 0, int(self.width / 2), 0)

    def get_cell(self, row, col) -> None | str:
        if 0 <= row < len(self.cells) and 0 <= col < len(self.cells[0]):
            return self.cells[row][col]
        return None

    def draw_piece(self, stdscr, shape, row, col, rot):
        for dr, dc in SHAPES[shape][rot]:
            if row + dr + self.x >= 0: # prevent from rendering above board
                stdscr.addstr(
                    row + dr + self.x,
                    (col + dc + self.y) * 2,
                    "██",
                    curses.color_pair(COLORS[shape]),
                )

    def draw(self, stdscr):
        fill_rect(
            stdscr,
            self.x,
            self.y * 2,
            self.x + self.height - 1,
            self.y * 2 + self.width - 1,
            8,
        )

        if self.show_next:
            self.draw_piece(
                stdscr, self.bag.get(self.piece_index + 1), 4, self.width + 3, 0
            )
            stdscr.addstr(1, (self.width + self.y) * 2 + 2, "NEXT PIECE:")

        self.draw_piece(
            stdscr, self.piece.shape, self.piece.row, self.piece.col, self.piece.rot
        )
        for row in range(self.height):
            for col in range(self.width):
                cell = self.get_cell(row, col)
                if cell not in (0, None):
                    stdscr.addstr(
                        row + self.x,
                        (col + self.y) * 2,
                        "██",
                        curses.color_pair(COLORS[cell]),
                    )

    def clear_lines(self) -> int:
        new_rows = [row for row in self.cells if not all(cell != 0 for cell in row)]
        lines_cleared = self.height - len(new_rows)
        for _ in range(lines_cleared):
            new_rows.insert(0, [0] * self.width)

        self.cells[:] = new_rows
        return lines_cleared

    def kill_piece(self):
        for dr, dc in SHAPES[self.piece.shape][self.piece.rot]:
            self.cells[dr + self.piece.row][dc + self.piece.col] = self.piece.shape
        self.clear_lines()

        self.piece_index += 1
        self.piece.shape = self.bag.get(self.piece_index)
        self.piece.row = 0
        self.piece.col = int(self.width / 2)
        self.piece.rot = 0

    def move_piece_down(self) -> bool:
        for dr, dc in SHAPES[self.piece.shape][self.piece.rot]:
            cell = self.get_cell(self.piece.row + dr + 1, self.piece.col + dc)
            if cell != 0:
                self.kill_piece()
                return False
        self.piece.row += 1
        return True

    def move_piece_right(self) -> bool:
        for dr, dc in SHAPES[self.piece.shape][self.piece.rot]:
            cell = self.get_cell(self.piece.row + dr, self.piece.col + dc + 1)
            if cell != 0:
                return False
        self.piece.col += 1
        return True

    def move_piece_left(self) -> bool:
        for dr, dc in SHAPES[self.piece.shape][self.piece.rot]:
            cell = self.get_cell(self.piece.row + dr, self.piece.col + dc - 1)
            if cell != 0:
                return False
        self.piece.col -= 1
        return True

    def rotate_piece(self) -> bool:
        new_rot = (self.piece.rot + 1) % 4
        for dr, dc in SHAPES[self.piece.shape][new_rot]:
            if self.get_cell(self.piece.row + dr, self.piece.col + dc) != 0:
                return False
        self.piece.rot = new_rot
        return True


class SevenBag:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.sequence = []

    def _extend(self):
        bag = list(SHAPES.keys())
        self.rng.shuffle(bag)
        self.sequence.extend(bag)

    def get(self, index: int) -> str:
        while index >= len(self.sequence):
            self._extend()
        return self.sequence[index]


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

    shared_bag = SevenBag()
    boards = [
        Board(0, 0, shared_bag),
        Board(0, 20, shared_bag, False),
    ]

    last_drop = time.time()
    drop_interval = 0.5
    selected_board = 0

    while True:
        key = stdscr.getch()
        if key == ord("q"):
            break
        if key == ord(" "):
            selected_board = (selected_board + 1) % len(boards)

        if key == ord("a"):
            boards[selected_board].move_piece_left()
        if key == ord("d"):
            boards[selected_board].move_piece_right()
        if key == ord("x"):
            boards[selected_board].rotate_piece()

        now = time.time()
        if now - last_drop >= drop_interval:
            for board in boards:
                board.move_piece_down()
            last_drop = now

        stdscr.clear()
        try:
            for board in boards:
                board.draw(stdscr)
        except curses.error:
            stdscr.clear()
            stdscr.addstr(0, 0, "Please expand console window.")

        stdscr.refresh()


curses.wrapper(main)
