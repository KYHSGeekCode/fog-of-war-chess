from typing import Optional

from fow_chess.piece import Piece, PieceType
from fow_chess.position import Position


class Move:
    def __init__(
        self,
        current_fen: str,
        piece: Piece,
        to_position: Position,
        capture_target: Optional[Piece] = None,
        castling_rook: Optional[Piece] = None,
        promotion_type: Optional[PieceType] = None,
    ):
        self.piece = piece
        self.to_position = to_position
        self.castling_rook = castling_rook
        self.promotion_piece = promotion_type
        self.capture_target = capture_target
        self.current_fen = current_fen

    def to_san(self):
        from fow_chess.board import Board

        board = Board(self.current_fen)
        san = ""

        # For handling castling
        if self.castling_rook is not None:
            if self.castling_rook.file > self.piece.file:  # Kingside
                return "O-O"
            else:  # Queenside
                return "O-O-O"

        # Determine if there's ambiguity
        ambiguous_moves = []
        if self.piece.type != PieceType.PAWN:
            for f in range(1, 9):  # Assuming 1-based indexing
                for r in range(1, 9):
                    other_piece = board.pieces.get(Position(file=f, rank=r))
                    if other_piece == self.piece:  # We found our own piece
                        continue
                    if (
                        other_piece
                        and other_piece.type == self.piece.type
                        and other_piece.color == self.piece.color
                    ):
                        possible_move = other_piece.generate_move(
                            self.current_fen, board, self.to_position
                        )  # Assuming pieces have such a method
                        if possible_move:
                            ambiguous_moves.append((f, r))

        if self.piece.type != PieceType.PAWN:
            san += self.piece.type.value

            # Handle ambiguities
            if len(ambiguous_moves) > 1:
                if all(m[0] == self.piece.file for m in ambiguous_moves):
                    san += str(self.piece.rank)
                else:
                    san += chr(ord("a") + self.piece.file - 1)

        if self.capture_target is not None:
            if self.piece.type == PieceType.PAWN:
                san += chr(ord("a") + self.piece.file - 1)
            san += "x"

        san += self.to_position.to_san()

        if self.promotion_piece is not None:
            san += "=" + self.promotion_piece.value

        return san

    def __str__(self):
        return self.to_san()

    def __repr__(self):
        return self.to_san()
