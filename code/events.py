from enum import Enum, auto


class UiEvent(Enum):
    INIT = auto()
    DRAW_TERRAIN = auto()
    DRAW_KEYS = auto()


class GameEvent(Enum):
    pass