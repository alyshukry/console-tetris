import random

from .constants import SHAPES
from .seven_bag import SevenBag
from .piece import Piece
from typing import Callable
from dataclasses import dataclass, field


@dataclass
class Board:
    bag: SevenBag
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


    def to_dict(self) -> dict:
        return {
            "cells": self.cells,
            "piece": {
                "shape": self.piece.shape,
                "row": self.piece.row,
                "col": self.piece.col,
                "rot": self.piece.rot,
            },
            "game_over": self.game_over,
            "height": self.height,
            "width": self.width,
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
        if self.on_lines_cleared:
            self.on_lines_cleared(lines_cleared)

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
        gap = random.randint(0, self.width - 1)
        for _ in range(n):
            self.cells.pop(0)  # remove top row to make room
            garbage_row = ["X" if col != gap else 0 for col in range(self.width)]
            self.cells.append(garbage_row)
