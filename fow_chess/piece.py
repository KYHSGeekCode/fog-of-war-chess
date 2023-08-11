from enum import Enum

from fow_chess.chesscolor import ChessColor
from fow_chess.pos_to_san import pos_to_san


class PieceType(Enum):
    PAWN = "p"
    KNIGHT = "n"
    BISHOP = "b"
    ROOK = "r"
    QUEEN = "q"
    KING = "k"


class Piece:
    def __init__(self, piece, rank, file):
        if piece.islower():
            self.color = ChessColor.BLACK
        else:
            self.color = ChessColor.WHITE
        self.type = PieceType(piece.lower())
        self.rank = rank
        self.file = file

    def __str__(self):
        return f"{self.color} {self.type.name} at {pos_to_san((self.rank, self.file))}"

    def __repr__(self):
        return str(self)
