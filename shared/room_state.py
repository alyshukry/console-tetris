from enum import Enum, auto


class RoomState(Enum):
    LOBBY = auto()
    COUNTDOWN = auto()
    IN_GAME = auto()
    RESULTS = auto()
