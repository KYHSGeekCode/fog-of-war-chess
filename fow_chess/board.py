from typing import Dict, List, Optional, Set

from fow_chess.chesscolor import ChessColor
from fow_chess.fen_parser import FenParser
from fow_chess.move import Move
from fow_chess.piece import Piece, PieceType
from fow_chess.position import Position


class Board:
    en_passant: Optional[Position]

    def to_fen(self) -> str:
        # Generate the piece placement string
        ranks = []
        for rank in range(8, 0, -1):  # start from 8 to 1
            empty_counter = 0
            rank_str = ""
            for file in range(1, 9):
                piece = self.pieces.get(Position(rank=rank, file=file))
                if piece:
                    if empty_counter:
                        rank_str += str(empty_counter)
                        empty_counter = 0
                    rank_str += (
                        piece.type.value.upper()
                        if piece.color == ChessColor.WHITE
                        else piece.type.value.lower()
                    )
                else:
                    empty_counter += 1
            if empty_counter:
                rank_str += str(empty_counter)
            ranks.append(rank_str)

        # Determine side to move
        side_to_move = "w" if self.side_to_move == ChessColor.WHITE else "b"

        # Determine castling rights
        castling_str = ""
        if self.castling[ChessColor.WHITE][0]:
            castling_str += "K"
        if self.castling[ChessColor.WHITE][1]:
            castling_str += "Q"
        if self.castling[ChessColor.BLACK][0]:
            castling_str += "k"
        if self.castling[ChessColor.BLACK][1]:
            castling_str += "q"
        if not castling_str:
            castling_str = "-"

        # Determine en passant target square
        en_passant_str = "-"
        if self.en_passant:
            en_passant_str = self.en_passant.to_san()

        # Convert the attributes to FEN format
        fen = " ".join(
            [
                "/".join(ranks),
                side_to_move,
                castling_str,
                en_passant_str,
                str(self.halfmove_clock),
                str(self.fullmove_number),
            ]
        )

        return fen

    def to_fow_fen(self, color: ChessColor) -> str:
        # get possible moves to get sight
        possible_moves = self.get_legal_moves(color)
        # calculate the sight
        sight: Set[Position] = set()
        for piece in self.pieces.values():
            if piece.color == color:
                sight.add(piece.position)
        for piece, moves in possible_moves.items():
            for move in moves:
                sight.add(move.to_position)
        # Generate the piece placement string
        ranks = []
        for rank in range(8, 0, -1):  # start from 8 to 1
            empty_counter = 0
            rank_str = ""
            for file in range(1, 9):
                piece = self.pieces.get(Position(rank=rank, file=file))
                if Position(rank=rank, file=file) in sight:
                    if piece:
                        if empty_counter:
                            rank_str += str(empty_counter)
                            empty_counter = 0

                        rank_str += (
                            piece.type.value.upper()
                            if piece.color == ChessColor.WHITE
                            else piece.type.value.lower()
                        )
                    else:
                        empty_counter += 1
                else:
                    if empty_counter:
                        rank_str += str(empty_counter)
                        empty_counter = 0
                    rank_str += "U"
            if empty_counter:
                rank_str += str(empty_counter)
            ranks.append(rank_str)

        # Determine side to move
        side_to_move = "w" if self.side_to_move == ChessColor.WHITE else "b"
        # Determine castling rights
        castling_str = ""
        if color == ChessColor.WHITE:
            if self.castling[ChessColor.WHITE][0]:
                castling_str += "K"
            if self.castling[ChessColor.WHITE][1]:
                castling_str += "Q"
        else:
            if self.castling[ChessColor.BLACK][0]:
                castling_str += "k"
            if self.castling[ChessColor.BLACK][1]:
                castling_str += "q"
        if not castling_str:
            castling_str = "-"

        # Determine en passant target square
        en_passant_str = "-"
        if self.en_passant and self.en_passant in sight:
            en_passant_str = self.en_passant.to_san()

        # Convert the attributes to FEN format
        fen = " ".join(
            [
                "/".join(ranks),
                side_to_move,
                castling_str,
                en_passant_str,
                "0",  # Hide halfmove clock in FOW
                str(self.fullmove_number),
            ]
        )
        return fen

    def __init__(self, fen: Optional[str] = None):
        if fen is None or fen == "":
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"  # starting position
        (
            pieces_on_all_ranks,
            side_to_move,
            castling,
            en_passant,
            self.halfmove_clock,
            self.fullmove_number,
        ) = FenParser(fen).parse()
        self.pieces: Dict[Position, Piece] = {}
        for rank in range(1, 9):
            for file in range(1, 9):
                piece = pieces_on_all_ranks[8 - rank][file - 1]
                if piece != " ":
                    pos = Position(rank=rank, file=file)
                    self.pieces[pos] = Piece(piece, pos)
        self.castling = {
            ChessColor.WHITE: ["K" in castling, "Q" in castling],
            ChessColor.BLACK: ["k" in castling, "q" in castling],
        }
        self.side_to_move = (
            ChessColor.WHITE if side_to_move == "w" else ChessColor.BLACK
        )
        if en_passant == "-":
            self.en_passant = None
        else:
            self.en_passant = Position.from_san(en_passant)
        self.halfmove_clock = int(self.halfmove_clock)
        self.fullmove_number = int(self.fullmove_number)
        self.fow_fen = self.to_fow_fen(self.side_to_move)
        self.fen = self.to_fen()
        # print("Initial fow fen = ", self.fow_fen)
        # print("Initial fen = ", self.fen)

    def __str__(self):
        parser = FenParser(self.fow_fen, fow_mark="U")
        (
            pieces_on_all_ranks,
            _,
            _,
            _,
            _,
            _,
        ) = parser.parse()

        res = ""
        for rank in range(8, 0, -1):
            for file in range(1, 9):
                piece = pieces_on_all_ranks[8 - rank][file - 1]
                res += piece
            res += "\n"
        return res

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

    # returns: The winner if the game is over, None otherwise
    def apply_move(self, move: Move) -> Optional[ChessColor]:
        # Remove the piece from its original position.
        del self.pieces[move.piece.position]
        # Handle captures.
        if move.capture_target:
            del self.pieces[move.capture_target.position]

        # update en passant
        self.en_passant = None
        if (
            move.piece.type == PieceType.PAWN
            and abs(move.piece.rank - move.to_position.rank) == 2
        ):
            self.en_passant = Position(
                rank=move.piece.rank - 1
                if move.piece.color == ChessColor.BLACK
                else move.piece.rank + 1,
                file=move.piece.file,
            )
        # Update the piece's position.
        move.piece.position = move.to_position
        # Add the piece to its new position.
        self.pieces[move.to_position] = move.piece
        # Handle promotion.
        if move.promotion_piece:
            move.piece.type = move.promotion_piece
        # Handle castling.
        if move.castling_rook:
            # Remove the rook from its original position.
            del self.pieces[move.castling_rook.position]

            # Define new rook positions based on king's end position
            if move.to_position == Position(
                rank=7, file=3
            ):  # Queenside castling for white
                new_rook_position = Position(rank=7, file=4)
            elif move.to_position == Position(
                rank=7, file=7
            ):  # Kingside castling for white
                new_rook_position = Position(rank=7, file=6)
            elif move.to_position == Position(
                rank=0, file=3
            ):  # Queenside castling for black
                new_rook_position = Position(rank=0, file=4)
            else:  # Kingside castling for black
                new_rook_position = Position(rank=0, file=6)

            # Update the rook's position.
            move.castling_rook.position = new_rook_position

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

        # switch side to move
        self.side_to_move = (
            ChessColor.WHITE
            if self.side_to_move == ChessColor.BLACK
            else ChessColor.BLACK
        )
        # update fullmove number
        if self.side_to_move == ChessColor.WHITE:
            self.fullmove_number += 1

        # update halfmove clock
        if move.piece.type == PieceType.PAWN or move.capture_target:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        self.fow_fen = self.to_fow_fen(self.side_to_move)
        self.fen = self.to_fen()
        if move.capture_target and move.capture_target.type == PieceType.KING:
            return move.piece.color

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
        target: Position,
        can_capture: bool = True,
        can_promote: bool = False,
        must_capture: bool = False,
    ) -> bool:
        if not target.is_valid():
            return True  # invalid target

        target_piece = self.pieces.get(target)
        if target_piece is None:
            if not must_capture:
                if can_promote:
                    for type in [
                        PieceType.QUEEN,
                        PieceType.ROOK,
                        PieceType.BISHOP,
                        PieceType.KNIGHT,
                    ]:
                        moves.append(Move(piece, target, promotion_type=type))
                else:
                    moves.append(Move(piece, target))
            return False
        else:
            if target_piece.color != piece.color and can_capture:
                if can_promote:
                    for type in [
                        PieceType.QUEEN,
                        PieceType.ROOK,
                        PieceType.BISHOP,
                        PieceType.KNIGHT,
                    ]:
                        moves.append(
                            Move(
                                piece,
                                target,
                                capture_target=target_piece,
                                promotion_type=type,
                            )
                        )
                else:
                    moves.append(Move(piece, target, capture_target=target_piece))
            return True

    def get_white_pawn_moves(self, piece: Piece) -> List[Move]:
        moves = []
        # march 1 or 2 : rank increases
        if piece.rank == 2:  # can move two squares
            if not self.add_move_if_not_blocked(
                moves, piece, Position(rank=3, file=piece.file), can_capture=False
            ):
                self.add_move_if_not_blocked(
                    moves, piece, Position(rank=4, file=piece.file), can_capture=False
                )
        elif piece.rank <= 7:  # can move only one squareø
            self.add_move_if_not_blocked(
                moves,
                piece,
                Position(rank=piece.rank + 1, file=piece.file),
                can_promote=piece.rank == 7,
                can_capture=False,
            )
        else:
            pass  # should have promoted
        # capture
        self.add_move_if_not_blocked(
            moves,
            piece,
            Position(rank=piece.rank + 1, file=piece.file + 1),
            can_promote=piece.rank == 7,
            can_capture=True,
            must_capture=True,
        )
        self.add_move_if_not_blocked(
            moves,
            piece,
            Position(rank=piece.rank + 1, file=piece.file - 1),
            can_promote=piece.rank == 7,
            can_capture=True,
            must_capture=True,
        )
        if self.en_passant:  # can capture en passant
            if (
                abs(piece.file - self.en_passant.file) == 1
                and piece.rank == 5
                and self.en_passant.rank == 6
            ):
                moves.append(
                    Move(
                        piece,
                        self.en_passant,
                        capture_target=self.pieces[
                            Position(rank=5, file=self.en_passant.file)
                        ],
                    )
                )
        # promotion: auto
        return moves

    def get_black_pawn_moves(self, piece: Piece) -> List[Move]:
        moves = []
        # march 1 or 2 : rank decreases
        if piece.rank == 7:  # can move two squares
            if not self.add_move_if_not_blocked(
                moves, piece, Position(rank=6, file=piece.file), can_capture=False
            ):
                self.add_move_if_not_blocked(
                    moves, piece, Position(rank=5, file=piece.file), can_capture=False
                )
        elif piece.rank >= 2:  # can move only one squareø
            self.add_move_if_not_blocked(
                moves,
                piece,
                Position(rank=piece.rank - 1, file=piece.file),
                can_promote=piece.rank == 2,
                can_capture=False,
            )
        else:
            pass  # should have promoted
        # capture
        self.add_move_if_not_blocked(
            moves,
            piece,
            Position(rank=piece.rank - 1, file=piece.file + 1),
            can_promote=piece.rank == 2,
            can_capture=True,
            must_capture=True,
        )
        self.add_move_if_not_blocked(
            moves,
            piece,
            Position(rank=piece.rank - 1, file=piece.file - 1),
            can_promote=piece.rank == 2,
            can_capture=True,
            must_capture=True,
        )
        if self.en_passant:  # can capture en passant
            if (
                abs(piece.file - self.en_passant.file) == 1
                and piece.rank == 4
                and self.en_passant.rank == 3
            ):
                moves.append(
                    Move(
                        piece,
                        self.en_passant,
                        capture_target=self.pieces[
                            Position(rank=4, file=self.en_passant.file)
                        ],
                    )
                )
        # promotion: auto
        return moves

    def get_knight_moves(self, piece: Piece) -> List[Move]:
        moves = []
        dx = [1, 2, 2, 1, -1, -2, -2, -1]
        dy = [2, 1, -1, -2, -2, -1, 1, 2]
        for i in range(8):
            target = Position(rank=piece.rank + dx[i], file=piece.file + dy[i])
            self.add_move_if_not_blocked(moves, piece, target, can_capture=True)
        return moves

    def get_bishop_moves(self, piece: Piece) -> List[Move]:
        moves = []
        # up right
        for i in range(1, 8):
            target = Position(rank=piece.rank + i, file=piece.file + i)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # up left
        for i in range(1, 8):
            target = Position(rank=piece.rank + i, file=piece.file - i)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # down right
        for i in range(1, 8):
            target = Position(rank=piece.rank - i, file=piece.file + i)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # down left
        for i in range(1, 8):
            target = Position(rank=piece.rank - i, file=piece.file - i)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        return moves

    def get_rook_moves(self, piece: Piece) -> List[Move]:
        moves = []
        # up
        for i in range(1, 8):
            target = Position(rank=piece.rank + i, file=piece.file)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # down
        for i in range(1, 8):
            target = Position(rank=piece.rank - i, file=piece.file)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # right
        for i in range(1, 8):
            target = Position(rank=piece.rank, file=piece.file + i)
            if self.add_move_if_not_blocked(moves, piece, target):
                break
        # left
        for i in range(1, 8):
            target = Position(rank=piece.rank, file=piece.file - i)
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
            target = Position(rank=piece.rank + dx[i], file=piece.file + dy[i])
            self.add_move_if_not_blocked(moves, piece, target, can_capture=True)
        # castling
        # king side rook (right rook)
        if self.castling[piece.color][0]:
            right_rook = self.pieces.get(Position(rank=piece.rank, file=8))
            if right_rook is not None:
                # check if there are no pieces between king and rook
                for file in range(piece.file + 1, right_rook.file):
                    if (
                        self.pieces.get(Position(rank=piece.rank, file=file))
                        is not None
                    ):
                        break
                else:
                    moves.append(
                        Move(
                            piece,
                            Position(rank=piece.rank, file=piece.file + 2),
                            castling_rook=right_rook,
                        )
                    )
        # queen side rook (left rook)
        if self.castling[piece.color][1]:
            left_rook = self.pieces.get(Position(rank=piece.rank, file=1))
            if left_rook is not None:
                # check if there are no pieces between king and rook
                for file in range(left_rook.file + 1, piece.file):
                    if (
                        self.pieces.get(Position(rank=piece.rank, file=file))
                        is not None
                    ):
                        break
                else:
                    moves.append(
                        Move(
                            piece,
                            Position(rank=piece.rank, file=piece.file - 2),
                            castling_rook=left_rook,
                        )
                    )
        return moves
