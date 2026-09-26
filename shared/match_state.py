from enum import Enum, auto
from net.protocol import broadcast_json


class MatchState(Enum):
    LOBBY = auto()
    COUNTDOWN = auto()
    IN_GAME = auto()
    RESULTS = auto()


async def set_match_state(match, new_state: "MatchState", extra: dict | None = None):
    match.state = new_state
    await broadcast_json(
        match, "match_state", {"state": new_state.value, **(extra or {})}
    )
