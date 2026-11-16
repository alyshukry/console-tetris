import time
from dataclasses import dataclass, field

from game.constants import TICKS_PER_SECOND
from game.piece import Piece
from net.serialization import deserialize_piece
from shared.room_state import RoomState


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


@dataclass
class PlayerState:
    boards: dict[int, BoardState] = field(default_factory=dict)
    my_id: int = -1
    room_state: RoomState = RoomState.LOBBY
    ready: bool = False
    player_count: int = 1
    ready_count: int = 0
    countdown: int = 5
    winners: list[int] = field(default_factory=list)
    tick: int = 0
    ticks_per_second: float = TICKS_PER_SECOND
    gravity_ticks: int = 10
    one_way_tick_estimate: float = 0.0
    pending_inputs: list[tuple[int, int, int]] = field(default_factory=list)
    latency: int = 60
    input_seq_by_tick: dict[int, int] = field(default_factory=dict)
    start_time: float = field(default_factory=time.monotonic)

    def reset_room(self):
        self.pending_inputs.clear()
        self.input_seq_by_tick.clear()
        self.one_way_tick_estimate = 0.0
