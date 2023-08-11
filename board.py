from typing import Dict, Tuple, List

from chesscolor import ChessColor
from fen_parser import FenParser
from move import Move
from piece import Piece, PieceType


class Board:
    def to_fen(self):
        raise NotImplementedError()

    def to_fow_fen(self):
        raise NotImplementedError()

    def __init__(
        self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    ):  # starting position
        (
            self.pieces_on_all_ranks,
            side_to_move,
            castling,
            self.en_passant,
            self.halfmove_clock,
            self.fullmove_number,
        ) = FenParser(fen).parse()
        self.pieces: Dict[Tuple[int, int], Piece] = {}
        for rank in range(1, 9):
            for file in range(1, 9):
                piece = self.pieces_on_all_ranks[8 - rank][file - 1]
                if piece != " ":
                    self.pieces[(rank, file)] = Piece(piece, rank, file)
        self.castling = {
            ChessColor.WHITE: ["K" in castling, "Q" in castling],
            ChessColor.BLACK: ["k" in castling, "q" in castling],
        }
        self.side_to_move = (
            ChessColor.WHITE if side_to_move == "w" else ChessColor.BLACK
        )

    def __str__(self):
        return "\n".join(
            ["".join(pieces_on_rank) for pieces_on_rank in self.pieces_on_all_ranks]
        )

    def __repr__(self):
        return str(self)

    def push_san(self, san: str):
        legal_moves = self.get_legal_moves(self.side_to_move)
        for piece, moves in legal_moves.items():
            for move in moves:
                if move.to_san() == san:
                    self.apply_move(move)
                    return
        raise Exception("Illegal move")

    def apply_move(self, move: Move):
        # Remove the piece from its original position.
        del self.pieces[(move.piece.rank, move.piece.file)]
        # Handle captures.
        if move.capture_target:
            del self.pieces[(move.capture_target.rank, move.capture_target.file)]
        # Update the piece's position.
        move.piece.rank, move.piece.file = move.to_position
        # Add the piece to its new position.
        self.pieces[move.to_position] = move.piece
        # Handle castling.
        if move.castling_rook:
            # Remove the rook from its original position.
            del self.pieces[(move.castling_rook.rank, move.castling_rook.file)]

            # Define new rook positions based on king's end position
            if move.to_position == (7, 3):  # Queenside castling for white
                new_rook_position = (7, 4)
            elif move.to_position == (7, 7):  # Kingside castling for white
                new_rook_position = (7, 6)
            elif move.to_position == (0, 3):  # Queenside castling for black
                new_rook_position = (0, 4)
            else:  # Kingside castling for black
                new_rook_position = (0, 6)

            # Update the rook's position.
            move.castling_rook.rank, move.castling_rook.file = new_rook_position

            # Place the rook in its new position.
            self.pieces[new_rook_position] = move.castling_rook

        # Update castling rights if needed (move a rook or king).
        if move.piece.type == PieceType.ROOK or move.piece.type == PieceType.KING:
            if move.piece.color == ChessColor.WHITE:
                if move.piece.rank == 7 and move.piece.file == 0:  # Left rook moved
                    self.castling[ChessColor.WHITE][0] = False
                if move.piece.rank == 7 and move.piece.file == 7:  # Right rook moved
                    self.castling[ChessColor.WHITE][1] = False
                if move.piece.type == PieceType.KING:
                    self.castling[ChessColor.WHITE] = [False, False]
            else:
                if move.piece.rank == 0 and move.piece.file == 0:  # Left rook moved
                    self.castling[ChessColor.BLACK][0] = False
                if move.piece.rank == 0 and move.piece.file == 7:  # Right rook moved
                    self.castling[ChessColor.BLACK][1] = False
                if move.piece.type == PieceType.KING:
                    self.castling[ChessColor.BLACK] = [False, False]

    def get_legal_moves(self, color: ChessColor) -> Dict[Piece, List[Move]]:
        legal_moves = {}
        for position, piece in self.pieces.items():
            if piece.color == color:
                if piece.type == PieceType.PAWN:
                    moves = self.get_pawn_moves(piece)
                elif piece.type == PieceType.KNIGHT:
                    moves = self.get_knight_moves(piece)
                elif piece.type == PieceType.BISHOP:
                    moves = self.get_bishop_moves(piece)
                elif piece.type == PieceType.ROOK:
                    moves = self.get_rook_moves(piece)
                elif piece.type == PieceType.QUEEN:
                    moves = self.get_queen_moves(piece)
                elif piece.type == PieceType.KING:
                    moves = self.get_king_moves(piece)
                else:
                    raise Exception("Unknown piece type")
                if moves:
                    legal_moves[piece] = moves
        return legal_moves

    def get_pawn_moves(self, piece: Piece) -> List[Move]:
        if piece.color == ChessColor.BLACK:
            return self.get_black_pawn_moves(piece)
        else:
            return self.get_white_pawn_moves(piece)

    # returns: was blocked
    def add_move_if_not_blocked(
        self,
        moves: List[Move],
        piece: Piece,
        target: Tuple[int, int],
        can_capture: bool = True,
        can_promote: bool = False,
        must_capture: bool = False,
    ) -> bool:
        if target[0] not in range(1, 9) or target[1] not in range(1, 9):
            return True  # invalid target

        target_piece = self.pieces.get(target)
        if target_piece is None:
            if not must_capture:
                moves.append(
                    Move(
                        piece,
                        target,
                        promotion_type=PieceType.PAWN if can_promote else None,
                    )
                )
            return False
        else:
            if target_piece.color != piece.color and can_capture:
                moves.append(
                    Move(
                        piece,
                        target,
                        capture_target=target_piece,
                        promotion_type=PieceType.PAWN if can_promote else None,
                    )
                )
            return True

    def get_white_pawn_moves(self, piece: Piece) -> List[Move]:
        moves = []
        # march 1 or 2 : rank increases
        if piece.rank == 2:  # can move two squares
            if not self.add_move_if_not_blocked(
                moves, piece, (3, piece.file), can_capture=False
            ):
                self.add_move_if_not_blocked(
                    moves, piece, (4, piece.file), can_capture=False
                )
        elif piece.rank <= 7:  # can move only one squareø
            self.add_move_if_not_blocked(
                moves,
                piece,
                (piece.rank + 1, piece.file),
                can_promote=piece.rank == 7,
                can_capture=False,
            )
        else:
            pass  # should have promoted
        # capture
        self.add_move_if_not_blocked(
            moves,
            piece,
            (piece.rank + 1, piece.file + 1),
            can_promote=piece.rank == 7,
            can_capture=True,
            must_capture=True,
        )
        self.add_move_if_not_blocked(
            moves,
            piece,
            (piece.rank + 1, piece.file - 1),
            can_promote=piece.rank == 7,
            can_capture=True,
            must_capture=True,
        )
        # TODO: en passant

        # promotion: auto
        return moves

    def get_black_pawn_moves(self, piece: Piece) -> List[Move]:
        moves = []
        # march 1 or 2 : rank decreases
        if piece.rank == 7:  # can move two squares
            if not self.add_move_if_not_blocked(
                moves, piece, (6, piece.file), can_capture=False
            ):
                self.add_move_if_not_blocked(
                    moves, piece, (5, piece.file), can_capture=False
                )
        elif piece.rank >= 2:  # can move only one squareø
            self.add_move_if_not_blocked(
                moves,
                piece,
                (piece.rank - 1, piece.file),
                can_promote=piece.rank == 2,
                can_capture=False,
            )
        else:
            pass  # should have promoted
        # capture
        self.add_move_if_not_blocked(
            moves,
            piece,
            (piece.rank - 1, piece.file + 1),
            can_promote=piece.rank == 2,
            can_capture=True,
            must_capture=True,
        )
        self.add_move_if_not_blocked(
            moves,
            piece,
            (piece.rank - 1, piece.file - 1),
            can_promote=piece.rank == 2,
            can_capture=True,
            must_capture=True,
        )
        # TODO: en passant

        # promotion: auto
        return moves

    def get_knight_moves(self, piece: Piece) -> List[Move]:
        moves = []
        dx = [1, 2, 2, 1, -1, -2, -2, -1]
        dy = [2, 1, -1, -2, -2, -1, 1, 2]
        for i in range(8):
            target = (piece.rank + dx[i], piece.file + dy[i])
            self.add_move_if_not_blocked(moves, piece, target, can_capture=True)
        return moves

    def get_bishop_moves(self, piece: Piece) -> List[Move]:
        moves = []
        # up right
        for i in range(1, 8):
            target = (piece.rank + i, piece.file + i)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # up left
        for i in range(1, 8):
            target = (piece.rank + i, piece.file - i)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # down right
        for i in range(1, 8):
            target = (piece.rank - i, piece.file + i)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # down left
        for i in range(1, 8):
            target = (piece.rank - i, piece.file - i)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        return moves

    def get_rook_moves(self, piece: Piece) -> List[Move]:
        moves = []
        # up
        for i in range(1, 8):
            target = (piece.rank + i, piece.file)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # down
        for i in range(1, 8):
            target = (piece.rank - i, piece.file)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # right
        for i in range(1, 8):
            target = (piece.rank, piece.file + i)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # left
        for i in range(1, 8):
            target = (piece.rank, piece.file - i)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        return moves

    def get_queen_moves(self, piece):
        return self.get_rook_moves(piece) + self.get_bishop_moves(piece)

    def get_king_moves(self, piece: Piece) -> List[Move]:
        moves = []
        dx = [1, 1, 1, 0, 0, -1, -1, -1]
        dy = [1, 0, -1, 1, -1, 1, 0, -1]
        for i in range(8):
            target = (piece.rank + dx[i], piece.file + dy[i])
            self.add_move_if_not_blocked(moves, piece, target, can_capture=True)
        # castling
        # king side rook (right rook)
        if self.castling[piece.color][0]:
            right_rook = self.pieces.get((piece.rank, 8))
            if right_rook is not None:
                # check if there are no pieces between king and rook
                for file in range(piece.file + 1, right_rook.file):
                    if self.pieces.get((piece.rank, file)) is not None:
                        break
                else:
                    moves.append(
                        Move(
                            piece,
                            (piece.rank, piece.file + 2),
                            castling_rook=right_rook,
                        )
                    )
        # queen side rook (left rook)
        if self.castling[piece.color][1]:
            left_rook = self.pieces.get((piece.rank, 1))
            if left_rook is not None:
                # check if there are no pieces between king and rook
                for file in range(left_rook.file + 1, piece.file):
                    if self.pieces.get((piece.rank, file)) is not None:
                        break
                else:
                    moves.append(
                        Move(
                            piece,
                            (piece.rank, piece.file - 2),
                            castling_rook=left_rook,
                        )
                    )
        return moves
