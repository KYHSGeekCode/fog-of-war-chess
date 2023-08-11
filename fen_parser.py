# Modified https://github.com/tlehman/fenparser/blob/master/fenparser.py
import re
from itertools import chain


class FenParser:
    def __init__(self, fen_str):
        self.fen_str = fen_str

    def parse(self):
        (
            placement,
            side_to_move,
            castling,
            en_passant,
            halfmove_clock,
            fullmove_number,
        ) = self.fen_str.split(" ")
        ranks = placement.split("/")
        pieces_on_all_ranks = [self.parse_rank(rank) for rank in ranks]
        return (
            pieces_on_all_ranks,
            side_to_move,
            castling,
            en_passant,
            halfmove_clock,
            fullmove_number,
        )

    def parse_rank(self, rank):
        rank_re = re.compile("(\d|[kqbnrpKQBNRP])")  # TODO: Added U (Unknown)
        piece_tokens = rank_re.findall(rank)
        pieces = self.flatten(map(self.expand_or_noop, piece_tokens))
        return pieces

    def flatten(self, lst):
        return list(chain(*lst))

    def expand_or_noop(self, piece_str):
        piece_re = re.compile("([kqbnrpKQBNRP])")  # TODO: Added U (Unknown)
        retval: str
        if piece_re.match(piece_str):
            retval = piece_str
        else:
            retval = self.expand(piece_str)
        return retval

    def expand(self, num_str):
        return int(num_str) * " "
