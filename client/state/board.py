from dataclasses import dataclass

from game.piece import Piece
from net.serialization import deserialize_piece


@dataclass
class BoardState:
    cells: list
    piece: Piece
    next_piece: Piece
    width: int = 10
    height: int = 20
    game_over: bool = False

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            cells=data["cells"],
            piece=deserialize_piece(data["piece"]),
            next_piece=deserialize_piece(data["next_piece"]),
            width=data["width"],
            height=data["height"],
            game_over=data["game_over"],
        )
