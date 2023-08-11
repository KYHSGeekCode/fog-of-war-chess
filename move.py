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
