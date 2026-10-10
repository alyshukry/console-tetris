from enum import StrEnum


class Action(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    ROTATE = "rotate"
    SOFT_DROP = "soft_drop"
    DROP = "drop"
