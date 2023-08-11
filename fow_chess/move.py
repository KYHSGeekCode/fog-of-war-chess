from typing import Tuple, Optional

from piece import Piece, PieceType


class Move:
    def __init__(
        self,
        piece: Piece,
        to_position: Tuple[int, int],
        capture_target: Optional[Piece] = None,
        castling_rook: Optional[Piece] = None,
        promotion_type: Optional[PieceType] = None,
    ):
        self.piece = piece
        self.to_position = to_position
        self.castling_rook = castling_rook
        self.promotion_piece = promotion_type
        self.capture_target = capture_target

    def to_san(self):
        san = ""
        if self.piece.type != PieceType.PAWN:
            san += self.piece.type.value
        if self.capture_target is not None:
            if self.piece.type == PieceType.PAWN:
                san += chr(ord("a") + self.piece.file)
            san += "x"
        san += chr(ord("a") + self.to_position[1] - 1)
        san += chr(ord("1") + self.to_position[0] - 1)
        if self.promotion_piece is not None:
            san += self.promotion_piece.value
        return san

    def __str__(self):
        return self.to_san()

    def __repr__(self):
        return self.to_san()
