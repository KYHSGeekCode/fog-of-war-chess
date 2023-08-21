from enum import Enum

from fow_chess.chesscolor import ChessColor
from fow_chess.position import Position


class PieceType(Enum):
    PAWN = "p"
    KNIGHT = "n"
    BISHOP = "b"
    ROOK = "r"
    QUEEN = "q"
    KING = "k"


class Piece:
    def __init__(self, piece, position: Position):
        if piece.islower():
            self.color = ChessColor.BLACK
        else:
            self.color = ChessColor.WHITE
        self.type = PieceType(piece.lower())
        self.position = position

    def __str__(self):
        return f"{self.color} {self.type.name} at {self.position}"

    def __repr__(self):
        return str(self)

    @property
    def rank(self):
        return self.position.rank

    @property
    def file(self):
        return self.position.file
