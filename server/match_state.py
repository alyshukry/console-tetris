from enum import Enum, auto


class MatchState(Enum):
    WAITING = auto()  # lobby, waiting for ready-ups
    COUNTDOWN = auto()  # everyone is ready, countdown started
    IN_PROGRESS = auto()  # game_loop/net_loop active
    RESULTS = auto()  # someone won, results shown
