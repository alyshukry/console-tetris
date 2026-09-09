from dataclasses import dataclass
from game.board import Board

@dataclass
class Client:
    board: Board
    id: int