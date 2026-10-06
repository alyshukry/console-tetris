from enum import Enum, auto


class MatchState(Enum):
    LOBBY = auto()
    COUNTDOWN = auto()
    IN_GAME = auto()
    RESULTS = auto()
