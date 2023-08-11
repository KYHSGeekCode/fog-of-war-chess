from enum import Enum

from chesscolor import ChessColor


class PieceType(Enum):
    PAWN = 0, "p"
    KNIGHT = 1, "n"
    BISHOP = 2, "b"
    ROOK = 3, "r"
    QUEEN = 4, "q"
    KING = 5, "k"


class Piece:
    def __init__(self, piece, rank, file):
        if piece.islower():
            self.color = ChessColor.BLACK
        else:
            self.color = ChessColor.WHITE
        self.type = PieceType[piece.lower()]
        self.rank = rank
        self.file = file
