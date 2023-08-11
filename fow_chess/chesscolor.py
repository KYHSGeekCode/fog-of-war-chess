from enum import Enum


class ChessColor(Enum):
    WHITE = 0
    BLACK = 1

    def __str__(self):
        return self.name.lower()
