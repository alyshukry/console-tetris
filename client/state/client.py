import time
from dataclasses import dataclass, field

from client.state.board import BoardState
from game.constants import TICKS_PER_SECOND
from shared.match_state import MatchState


@dataclass
class ClientState:
    boards: dict[int, BoardState] = field(default_factory=dict)
    my_id: int = -1
    match_state: MatchState = MatchState.LOBBY
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

    def reset_match(self):
        self.pending_inputs.clear()
        self.input_seq_by_tick.clear()
        self.one_way_tick_estimate = 0.0
