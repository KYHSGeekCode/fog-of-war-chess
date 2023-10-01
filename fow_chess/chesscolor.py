from enum import Enum


class ChessColor(Enum):
    WHITE = 0
    BLACK = 1
    DRAW = 2

    def __str__(self):
        return self.name.lower()
