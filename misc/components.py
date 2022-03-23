from enum import Enum, auto
from dataclasses import dataclass


class Screens(Enum):
    MAIN = auto()
    SETTINGS = auto()
    HELP = auto()


class GameStates(Enum):
    WIN = 'win'
    LOSE = 'lose'
    MOVE = 'move'
    IDLE = 'ok'


@dataclass
class GamePreset:
    field_size: tuple[int, int]
    mines_count: int


@dataclass
class LayoutPreset:
    left_indent: int = 15
    top_indent: int = 94
    cell_size: int = 30
    field_indent: int = 5
    indicator_size: int = 50
    counter_width: int = 82
    menubar_height: int = 20
