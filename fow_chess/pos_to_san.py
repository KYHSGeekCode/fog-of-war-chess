from typing import Tuple


# rank, file
def pos_to_san(pos: Tuple[int, int]):
    return chr(ord("a") + pos[1] - 1) + chr(ord("1") + pos[0] - 1)
