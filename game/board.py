import random
from dataclasses import dataclass, field

from .collision import fits, fits_abs
from .constants import SHAPES
from .piece import Piece
from .seven_bag import SevenBag


@dataclass
class MoveResult:
    moved: bool
    locked: bool
    lines_cleared: int
    game_over: bool


@dataclass
class Board:
    bag: SevenBag
    piece_index: int = 0
    height: int = 20
    width: int = 10
    game_over: bool = False
    cells: list[list[int | str]] = field(init=False)
    piece: Piece = field(init=False)

    def __post_init__(self):
        self.cells = [[0] * self.width for _ in range(self.height)]
        self.piece = Piece(self.bag.get(0), 0, int(self.width / 2), 0)

    def clear_lines(self) -> int:
        new_rows = [row for row in self.cells if not all(cell != 0 for cell in row)]
        lines_cleared = self.height - len(new_rows)

        for _ in range(lines_cleared):
            new_rows.insert(0, [0] * self.width)

        self.cells[:] = new_rows

        return lines_cleared

    def lock_piece(self):
        cells = [
            (dr + self.piece.row, dc + self.piece.col)
            for dr, dc in SHAPES[self.piece.shape][self.piece.rot]
        ]

        if any(r < 0 for r, _ in cells):  # lock out
            self.lose()
            return MoveResult(False, True, 0, True)

        for r, c in cells:
            self.cells[r][c] = self.piece.shape

        lines_cleared = self.clear_lines()
        spawn_ok = self.spawn_piece()
        return MoveResult(False, True, lines_cleared, not spawn_ok)

    def spawn_piece(self) -> bool:
        if self.game_over:
            return False

        self.piece_index += 1
        candidate = Piece(self.bag.get(self.piece_index), 0, self.width // 2, 0)

        if not fits_abs(
            self.cells, candidate, self.width, self.height, candidate.row, candidate.col
        ):
            self.lose()
            return False

        self.piece = candidate
        return True

    def lose(self):
        self.game_over = True

    def move_piece_down(self):
        if fits(self.cells, self.piece, self.width, self.height, 1, 0):
            self.piece.row += 1
            return MoveResult(True, False, 0, False)
        return self.lock_piece()

    def move_piece_right(self):
        if fits(self.cells, self.piece, self.width, self.height, 0, 1):
            self.piece.col += 1
            return MoveResult(True, False, 0, False)
        return MoveResult(False, False, 0, False)

    def move_piece_left(self):
        if fits(self.cells, self.piece, self.width, self.height, 0, -1):
            self.piece.col -= 1
            return MoveResult(True, False, 0, False)
        return MoveResult(False, False, 0, False)

    def drop_piece(self):
        result = self.move_piece_down()
        while result.moved:
            result = self.move_piece_down()
        return result

    def soft_drop_piece(self):
        return self.move_piece_down()

    def rotate_piece(self):
        new_rot = (self.piece.rot + 1) % 4
        if fits(
            self.cells,
            self.piece,
            self.width,
            self.height,
            0,
            0,
            rot=new_rot,
        ):
            self.piece.rot = new_rot
            return MoveResult(True, False, 0, False)
        return MoveResult(False, False, 0, False)

    def add_garbage(self, n: int):
        if any(any(c != 0 for c in row) for row in self.cells[:n]):
            self.lose()
        gap = random.randint(0, self.width - 1)
        for _ in range(n):
            self.cells.pop(0)  # remove top row to make room
            garbage_row = ["X" if col != gap else 0 for col in range(self.width)]
            self.cells.append(garbage_row)
        while not fits(self.cells, self.piece, self.width, self.height, 0, 0):
            self.piece.row -= 1
            if self.piece.row < -2:
                self.lose()
                break
