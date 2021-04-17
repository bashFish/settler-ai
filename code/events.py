from enum import Enum, auto


class UiEvent(Enum):
    INIT = auto()
    DRAW_TERRAIN = auto()
    DRAW_KEYS = auto()
    ADD_BUILDING = auto()


class GameEvent(Enum):
    ADD_BUILDING = auto()
