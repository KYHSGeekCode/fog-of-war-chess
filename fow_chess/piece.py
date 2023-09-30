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

    @property
    def ordinal(self):
        return {
            PieceType.PAWN: 0,
            PieceType.KNIGHT: 1,
            PieceType.BISHOP: 2,
            PieceType.ROOK: 3,
            PieceType.QUEEN: 4,
            PieceType.KING: 5,
        }[self]


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

    def __eq__(self, other):
        if other is None:
            return False
        return (
            self.color == other.color
            and self.type == other.type
            and self.position == other.position
        )

    def __hash__(self):
        return hash((self.color, self.type, self.position))

    @property
    def rank(self):
        return self.position.rank

    @property
    def file(self):
        return self.position.file

    def generate_move(self, current_fen: str, board: "Board", to: Position) -> "Move":
        from fow_chess.move import Move

        def is_path_clear(start: Position, end: Position) -> bool:
            """Check if the path between start and end is clear of pieces."""
            delta_file = end.file - start.file
            delta_rank = end.rank - start.rank
            file_step = 0 if delta_file == 0 else (1 if delta_file > 0 else -1)
            rank_step = 0 if delta_rank == 0 else (1 if delta_rank > 0 else -1)

            current = Position(file=start.file + file_step, rank=start.rank + rank_step)
            while current != end:
                from fow_chess import board

                if board.pieces.get(
                    Position(current.file, current.rank)
                ):  # Assuming 1-based indexing
                    return False
                current = Position(
                    file=current.file + file_step, rank=current.rank + rank_step
                )
            return True

        # This method is not used when this is a PAWN
        if self.type == PieceType.PAWN:
            if self.color == ChessColor.WHITE:
                if self.position.rank == 2:
                    if to.rank == 3 or to.rank == 4:
                        return Move(current_fen, self, to)
                else:
                    if to.rank == self.position.rank + 1:
                        return Move(current_fen, self, to)
            else:
                if self.position.rank == 7:
                    if to.rank == 6 or to.rank == 5:
                        return Move(current_fen, self, to)
                else:
                    if to.rank == self.position.rank - 1:
                        return Move(current_fen, self, to)
        elif self.type == PieceType.KNIGHT:
            if (
                abs(self.position.rank - to.rank) == 2
                and abs(self.position.file - to.file) == 1
            ) or (
                abs(self.position.rank - to.rank) == 1
                and abs(self.position.file - to.file) == 2
            ):
                return Move(current_fen, self, to)
        elif self.type == PieceType.BISHOP:
            if abs(self.position.rank - to.rank) == abs(
                self.position.file - to.file
            ) and is_path_clear(self.position, to):
                # check if there is a piece in the way
                return Move(current_fen, self, to)
        elif self.type == PieceType.ROOK:
            if (
                self.position.rank == to.rank or self.position.file == to.file
            ) and is_path_clear(self.position, to):
                # check if there is a piece in the way
                return Move(current_fen, self, to)
        elif self.type == PieceType.QUEEN:
            if (
                abs(self.position.rank - to.rank) == abs(self.position.file - to.file)
                or self.position.rank == to.rank
                or self.position.file == to.file
            ) and is_path_clear(self.position, to):
                # check if there is a piece in the way
                return Move(current_fen, self, to)
        elif self.type == PieceType.KING:
            # Should not be needed, but just in case
            if (
                abs(self.position.rank - to.rank) <= 1
                and abs(self.position.file - to.file) <= 1
            ):
                return Move(current_fen, self, to)
        return None
