from dataclasses import dataclass, field
from game.board import Board

@dataclass
class Client:
    board: Board
    id: int
    ready: bool = False
    outbox: list[tuple[str, dict]] = field(default_factory=list)
    input_queue: list[tuple[int, str]] = field(default_factory=list)