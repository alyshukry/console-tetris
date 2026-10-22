from dataclasses import dataclass, field

from game.board import Board
from shared.action import Action


@dataclass
class Player:
    board: Board
    player_id: int
    ready: bool = False
    outbox: list[tuple[str, dict]] = field(default_factory=list)
    input_queue: list[tuple[int, int, Action]] = field(default_factory=list)
    last_processed_input_tick: int = -1
    last_processed_input_seq: int = -1
