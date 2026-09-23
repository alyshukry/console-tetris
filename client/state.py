from dataclasses import dataclass, field
from server.match import MatchState


@dataclass
class ClientState:
    boards: dict[int, dict] = field(default_factory=dict)
    my_id: int = -1
    gravity: float = 0.25
    match_state: MatchState = MatchState.WAITING
    ready: bool = False
    player_count: int = 1
    ready_count: int = 0
    countdown: int = 5
    winners: list[int] = field(default_factory=list)
