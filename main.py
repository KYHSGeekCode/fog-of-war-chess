from board import Board
from pos_to_san import pos_to_san


def main():
    board = Board()
    # board = Board("8/5N2/4p2p/5p1k/1p4rP/1P2Q1P1/P4P1K/5q2 w - - 15 44")
    while True:
        print(board)
        print(f"Turn: {board.side_to_move}")
        pieces_str = ", ".join(
            [f"{pos_to_san(pos)}: {piece}" for pos, piece in board.pieces.items()]
        )
        # print(f"Pieces: {pieces_str}")
        print("Legal moves: ", board.get_legal_moves(board.side_to_move))
        move = input("Enter move: ")
        # board.push_san(move)


if __name__ == "__main__":
    main()
