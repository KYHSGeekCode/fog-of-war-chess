class Position:
    def __init__(self, file, rank):
        self.file = file
        self.rank = rank

    def to_san(self) -> str:
        return chr(ord("a") + self.file - 1) + chr(ord("1") + self.rank - 1)

    def __str__(self):
        return self.to_san()

    def __repr__(self):
        return str(self)

    @staticmethod
    def from_san(san: str):
        san = san.lower()
        return Position(
            file=ord(san[0]) - ord("a") + 1, rank=ord(san[1]) - ord("1") + 1
        )

    def is_valid(self) -> bool:
        return self.file in range(1, 9) and self.rank in range(1, 9)
