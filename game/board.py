import random

from .constants import SHAPES
from .seven_bag import SevenBag
from .piece import Piece
from .collision import fits, fits_abs
from typing import Callable
from dataclasses import dataclass, field, asdict


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

    def to_dict(self) -> dict:
        return {
            "cells": self.cells,
            "width": self.width,
            "height": self.height,
            "piece": asdict(self.piece),
            "next_piece": self.bag.get(
                self.piece_index + 1
            ),  # since player has no bag access
            "game_over": self.game_over,
        }

    def get_cell(self, row, col) -> None | str:
        if 0 <= row < len(self.cells) and 0 <= col < len(self.cells[0]):
            return self.cells[row][col]
        return None

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

        lines_cleared = self.clear_lines()
        spawn_ok = self.spawn_piece()
        return MoveResult(False, True, lines_cleared, not spawn_ok)

    def spawn_piece(self) -> bool:
        if not self.game_over:
            self.piece_index += 1
            self.piece.shape = self.bag.get(self.piece_index)
            if not fits_abs(
                self.cells, asdict(self.piece), self.width, self.height, 0, int(self.width / 2)
            ):
                self.lose()
                return False
            self.piece.row = 0
            self.piece.col = int(self.width / 2)
            self.piece.rot = 0
            return True
        return False

    def lose(self):
        self.game_over = True
        return MoveResult(False, False, 0, True)

    def move_piece_down(self):
        if fits(self.cells, asdict(self.piece), self.width, self.height, 1, 0):
            self.piece.row += 1
            return MoveResult(True, False, 0, False)
        return self.kill_piece()

    def move_piece_right(self):
        if fits(self.cells, asdict(self.piece), self.width, self.height, 0, 1):
            self.piece.col += 1
            return MoveResult(True, False, 0, False)
        return MoveResult(False, False, 0, False)

    def move_piece_left(self):
        if fits(
            self.cells, asdict(self.piece), self.width, self.height, 0, -1
        ):
            self.piece.col -= 1
            return MoveResult(True, False, 0, False)
        return MoveResult(False, False, 0, False)

    def drop_piece(self):
        while self.move_piece_down().moved:
            pass

    def soft_drop_piece(self):
        self.move_piece_down() # already does on_piece_moved

    def rotate_piece(self):
        new_rot = (self.piece.rot + 1) % 4
        if fits(
            self.cells,
            asdict(self.piece),
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
        gap = random.randint(0, self.width - 1)
        for _ in range(n):
            self.cells.pop(0)  # remove top row to make room
            garbage_row = ["X" if col != gap else 0 for col in range(self.width)]
            self.cells.append(garbage_row)
