import random

from .constants import SHAPES
from .seven_bag import SevenBag
from .piece import Piece
from .collision import fits
from typing import Callable
from dataclasses import dataclass, field, asdict


@dataclass
class Board:
    bag: SevenBag
    piece_index: int = 0
    height: int = 20
    width: int = 10
    game_over: bool = False
    cells: list[list[int | str]] = field(init=False)
    piece: Piece = field(init=False)
    on_piece_moved: Callable[[], None] | None = None
    on_piece_killed: Callable[[int], None] | None = None

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
            ),  # since client has no bag access
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
        self.spawn_piece()

        if self.on_piece_killed:
            self.on_piece_killed(lines_cleared)

    def spawn_piece(self) -> bool:
        if not self.game_over:
            self.piece_index += 1
            self.piece.shape = self.bag.get(self.piece_index)
            self.piece.row = 0
            self.piece.col = int(self.width / 2)
            self.piece.rot = 0
            if not fits(
                self.cells, self.to_dict().get("piece"), self.width, self.height, 0, 0
            ):
                self.lose()
                return False
            return True
        return False

    def lose(self):
        self.game_over = True

    def move_piece_down(self) -> bool:
        if fits(self.cells, self.to_dict().get("piece"), self.width, self.height, 1, 0):
            self.piece.row += 1
            return True
        self.kill_piece()
        return False

    def move_piece_right(self) -> bool:
        if fits(self.cells, self.to_dict().get("piece"), self.width, self.height, 0, 1):
            self.piece.col += 1
            if self.on_piece_moved:
                self.on_piece_moved()
            return True
        return False

    def move_piece_left(self) -> bool:
        if fits(
            self.cells, self.to_dict().get("piece"), self.width, self.height, 0, -1
        ):
            self.piece.col -= 1
            if self.on_piece_moved:
                self.on_piece_moved()
            return True
        return False

    def drop_piece(self):
        while self.move_piece_down():
            pass

    def soft_drop_piece(self):
        self.move_piece_down()
        if self.on_piece_moved:
            self.on_piece_moved()

    def rotate_piece(self) -> bool:
        new_rot = (self.piece.rot + 1) % 4
        if fits(
            self.cells,
            self.to_dict().get("piece"),
            self.width,
            self.height,
            0,
            0,
            rot=new_rot,
        ):
            self.piece.rot = new_rot
            if self.on_piece_moved:
                self.on_piece_moved()
            return True
        return False

    def add_garbage(self, n: int):
        gap = random.randint(0, self.width - 1)
        for _ in range(n):
            self.cells.pop(0)  # remove top row to make room
            garbage_row = ["X" if col != gap else 0 for col in range(self.width)]
            self.cells.append(garbage_row)
