from dataclasses import dataclass, field
from game.constants import TICKS_PER_SECOND
from server.match import MatchState


@dataclass
class ClientState:
    boards: dict[int, dict] = field(default_factory=dict)
    my_id: int = -1
    gravity: float = 0.25
    match_state: MatchState = MatchState.LOBBY
    ready: bool = False
    player_count: int = 1
    ready_count: int = 0
    countdown: int = 5
    winners: list[int] = field(default_factory=list)
    tick: int = 0
    ticks_per_second: float = TICKS_PER_SECOND
    gravity_ticks: int = 10
    tick_offset: int = 0
    rtt_estimate: float = 0.0
    pending_inputs: dict[int, int] = field(default_factory=dict)