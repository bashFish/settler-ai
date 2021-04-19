from enum import Enum, auto


class UiEvent(Enum):
    INIT = auto()
    DRAW_TERRAIN = auto()
    DRAW_KEYS = auto()
    ADD_BUILDING = auto()
    DELETE_CELL = auto()
    DRAW_DASHBOARD = auto()


class GameEvent(Enum):
    _ADD_BUILDING = auto()
    CONSTRUCT_BUILDING = auto()
    DROP = auto()
    END_GAME = auto()
