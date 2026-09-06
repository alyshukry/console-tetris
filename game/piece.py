from dataclasses import dataclass

@dataclass
class Piece:
    shape: str
    row: int
    col: int
    rot: int