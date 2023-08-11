from board import Board


def main():
    board = Board()
    # board = Board("8/5N2/4p2p/5p1k/1p4rP/1P2Q1P1/P4P1K/5q2 w - - 15 44")
    while True:
        print(board)
        print(f"Turn: {board.side_to_move}")
        print(f"En passant: {board.en_passant}")
        legal_moves = board.get_legal_moves(board.side_to_move)
        move_candidates = []
        for moves in legal_moves.values():
            for move in moves:
                move_candidates.append(move)
        print(
            f"Move candidates: ",
            ",".join(
                [f"{i}: {move.to_san()}" for i, move in enumerate(move_candidates)]
            ),
        )
        str_move = input("Enter move: ")
        if str_move == "q":
            break
        move = int(str_move)
        selected_move = move_candidates[move]
        print(f"Selected move: {selected_move}")
        # board.push_san(move)
        board.apply_move(selected_move)


if __name__ == "__main__":
    main()
