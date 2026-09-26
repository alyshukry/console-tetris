from dataclasses import dataclass

from game.piece import Piece

@dataclass
class BoardState:
    cells: list
    piece: Piece
    next_piece: Piece
    width: int = 10
    height: int = 20
    game_over: bool = False