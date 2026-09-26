from dataclasses import dataclass, field
from game.board import Board

@dataclass
class Player:
    board: Board
    id: int
    ready: bool = False
    outbox: list[tuple[str, dict]] = field(default_factory=list)
    input_queue: list[tuple[int, str]] = field(default_factory=list)
    last_processed_input_tick: int = -1