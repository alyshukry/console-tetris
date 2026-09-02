import curses
import time
import random
from dataclasses import dataclass, field
from typing import Callable

SHAPES = {
    "I": [
        [(-1, -2), (-1, -1), (-1, 0), (-1, 1)],  # 0°
        [(-2, 0), (-1, 0), (0, 0), (1, 0)],  # R (90° CW)
        [(0, -2), (0, -1), (0, 0), (0, 1)],  # 180°
        [(-2, -1), (-1, -1), (0, -1), (1, -1)],  # L (270°)
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
    "O": [
        [(0, 0), (0, -1), (-1, 0), (-1, -1)],  # same at every rotation
    ]
    * 4,
    "S": [
        [(0, 0), (-1, 0), (-1, 1), (0, -1)],  # 0°
        [(0, 0), (0, 1), (-1, 0), (1, 1)],  # R
        [(0, 0), (0, 1), (1, -1), (1, 0)],  # 180°
        [(0, 0), (-1, -1), (1, 0), (0, -1)],  # L
    ],
    "T": [
        [(0, 0), (0, 1), (0, -1), (-1, 0)],  # 0°
        [(0, 0), (0, 1), (1, 0), (-1, 0)],  # R
        [(0, 0), (1, 0), (0, 1), (0, -1)],  # 180°
        [(0, 0), (0, -1), (1, 0), (-1, 0)],  # L
    ],
    "Z": [
        [(0, 0), (-1, 0), (-1, -1), (0, 1)],  # 0°
        [(0, 0), (0, 1), (1, 0), (-1, 1)],  # R
        [(0, 0), (0, -1), (1, 1), (1, 0)],  # 180°
        [(0, 0), (1, -1), (-1, 0), (0, -1)],  # L
    ],
}

COLORS = {
    "I": 1,
    "J": 2,
    "L": 7,
    "O": 3,
    "S": 5,
    "T": 4,
    "Z": 6,
    "X": 9,
}


@dataclass
class Piece:
    shape: str
    row: int
    col: int
    rot: int


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


@dataclass
class Board:
    x: int
    y: int
    bag: SevenBag
    show_next: bool = True
    piece_index: int = 0
    height: int = 20
    width: int = 10
    game_over: bool = False
    cells: list[list[int | str]] = field(init=False)
    piece: Piece = field(init=False)
    on_lines_cleared: Callable[[int], None] | None = None

    def __post_init__(self):
        self.cells = [[0] * self.width for _ in range(self.height)]
        self.piece = Piece(self.bag.get(0), 0, int(self.width / 2), 0)

    def get_cell(self, row, col) -> None | str:
        if 0 <= row < len(self.cells) and 0 <= col < len(self.cells[0]):
            return self.cells[row][col]
        return None

    def draw(self, stdscr):
        fill_rect(
            stdscr,
            self.x,
            self.y * 2,
            self.x + self.height - 1,
            self.y * 2 + self.width - 1,
            10,
        )
        self.draw_border(stdscr)

        if self.show_next:
            self.draw_piece(
                stdscr, self.bag.get(self.piece_index + 1), 4, self.width + 3, 0
            )
            stdscr.addstr(self.x + 1, (self.width + self.y) * 2 + 2, "NEXT PIECE:")

        if not self.game_over:
            self.draw_ghost(stdscr)
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
                        curses.color_pair(9 if self.game_over else COLORS[cell]),
                    )

    def draw_piece(self, stdscr, shape, row, col, rot):
        for dr, dc in SHAPES[shape][rot]:
            if row + dr + self.x > 0:  # prevent from rendering above board
                stdscr.addstr(
                    row + dr + self.x,
                    (col + dc + self.y) * 2,
                    "██",
                    curses.color_pair(9 if self.game_over else COLORS[shape]),
                )

    def draw_ghost(self, stdscr):
        ghost_row = self.piece.row + self.get_ghost_row()
        for dr, dc in SHAPES[self.piece.shape][self.piece.rot]:
            stdscr.addstr(
                ghost_row + dr + self.x,
                (self.piece.col + dc + self.y) * 2,
                "░░",
                curses.color_pair(COLORS[self.piece.shape]),
            )

    def draw_border(self, stdscr):
        top = self.x - 1
        left = (self.y * 2) - 1
        bottom = self.x + self.height
        right = self.y * 2 + self.width * 2

        stdscr.addstr(top, left, "┌" + "─" * (self.width * 2) + "┐")
        stdscr.addstr(top, left + 2, " USRNM ")
        for row in range(self.height):
            stdscr.addstr(self.x + row, left, "│")
            stdscr.addstr(self.x + row, right, "│")
        stdscr.addstr(bottom, left, "└" + "─" * (self.width * 2) + "┘")

    def clear_lines(self) -> int:
        new_rows = [row for row in self.cells if not all(cell != 0 for cell in row)]
        lines_cleared = self.height - len(new_rows)
        for _ in range(lines_cleared):
            new_rows.insert(0, [0] * self.width)

        self.cells[:] = new_rows
        if self.on_lines_cleared: self.on_lines_cleared(lines_cleared)
        
        return lines_cleared

    def kill_piece(self):
        for dr, dc in SHAPES[self.piece.shape][self.piece.rot]:
            self.cells[dr + self.piece.row][dc + self.piece.col] = self.piece.shape
        self.clear_lines()
        self.spawn_piece()

    def spawn_piece(self) -> bool:
        if not self.game_over:
            self.piece_index += 1
            self.piece.shape = self.bag.get(self.piece_index)
            self.piece.row = 0
            self.piece.col = int(self.width / 2)
            self.piece.rot = 0
            if not self.fits(0, 0):
                self.lose()
                return False
            return True
        return False

    def lose(self):
        self.game_over = True

    def fits(self, drow: int, dcol: int, rot: int | None = None) -> bool:
        rot = self.piece.rot if rot is None else rot
        for dr, dc in SHAPES[self.piece.shape][rot]:
            row = self.piece.row + dr + drow
            col = self.piece.col + dc + dcol
            if col < 0 or col >= self.width or row >= self.height:
                return False  # out of bounds sideways or below: blocked
            if row < 0:
                continue  # above the board: allowed
            if self.cells[row][col] != 0:
                return False
        return True

    def move_piece_down(self) -> bool:
        if self.fits(1, 0):
            self.piece.row += 1
            return True
        self.kill_piece()
        return False

    def move_piece_right(self) -> bool:
        if self.fits(0, 1):
            self.piece.col += 1
            return True
        return False

    def move_piece_left(self) -> bool:
        if self.fits(0, -1):
            self.piece.col -= 1
            return True
        return False

    def drop_piece(self):
        while self.move_piece_down():
            pass

    def rotate_piece(self) -> bool:
        new_rot = (self.piece.rot + 1) % 4
        if self.fits(0, 0, rot=new_rot):
            self.piece.rot = new_rot
            return True
        return False

    def get_ghost_row(self) -> int:
        ghost_row = 0
        while self.fits(ghost_row + 1, 0):
            ghost_row += 1
        return ghost_row
    
    def add_garbage(self, n: int):
        for _ in range(n):
            self.cells.pop(0)  # remove top row to make room
            gap = random.randint(0, self.width - 1)
            garbage_row = ["X" if col != gap else 0 for col in range(self.width)]
            self.cells.append(garbage_row)

def make_lines_cleared_handler(board, all_boards) -> Callable[[int], None]:
    def handler(lines_cleared):
        print(send_garbage(board, all_boards, lines_cleared))
    return handler

def send_garbage(sender: Board, recipients: list[Board], lines: int) -> int:
    if lines <= 1:
        return 0 # single-line clears don't send garbage

    opponents = [b for b in recipients if b is not sender and not b.game_over]
    if not opponents:
        return 0

    total_garbage = lines - 1  # simplified formula
    per_board = total_garbage // len(opponents)
    remainder = total_garbage % len(opponents)

    for i, board in enumerate(opponents):
        amount = per_board + (1 if i < remainder else 0)
        if amount > 0:
            board.add_garbage(amount)
            return amount
    return 0

def fill_rect(stdscr, y1, x1, y2, x2, color_pair):
    for y in range(y1, y2 + 1):
        width = x2 - x1 + 1
        stdscr.addstr(y, x1, "██" * width, curses.color_pair(color_pair))


def main(stdscr):
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

    curses.init_pair(1, 20, curses.COLOR_BLACK)  # I
    curses.init_pair(2, 21, curses.COLOR_BLACK)  # J
    curses.init_pair(3, 23, curses.COLOR_BLACK)  # O
    curses.init_pair(4, 25, curses.COLOR_BLACK)  # T
    curses.init_pair(5, 24, curses.COLOR_BLACK)  # S
    curses.init_pair(6, 26, curses.COLOR_BLACK)  # Z
    curses.init_pair(7, 22, curses.COLOR_BLACK)  # L
    curses.init_pair(9, 28, curses.COLOR_BLACK)  # gray
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_BLACK)  # black

    shared_bag = SevenBag()
    boards = [
        Board(1, 1, shared_bag),
        Board(1, 21, shared_bag, show_next=False),
    ]
    for board in boards: make_lines_cleared_handler(board, boards)

    last_drop = time.time()
    drop_interval = 0.5
    selected_board = 0

    while True:
        key = stdscr.getch()
        if key == ord("q"):
            break
        if key == ord("p"):
            selected_board = (selected_board + 1) % len(boards)

        if not boards[selected_board].game_over:
            if key == curses.KEY_LEFT:
                boards[selected_board].move_piece_left()
            if key == curses.KEY_RIGHT:
                boards[selected_board].move_piece_right()
            if key == curses.KEY_UP:
                boards[selected_board].rotate_piece()
            if key == curses.KEY_DOWN:
                boards[selected_board].move_piece_down()
                last_drop = time.time()
            if key == ord(" "):
                boards[selected_board].drop_piece()

        now = time.time()
        if now - last_drop >= drop_interval:
            for board in boards:
                if not board.game_over:
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
