from rand import *
from typing import List, Tuple

class CellDungeon:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.map = []  # type: List[List[str]]

    def clear(self):
        self.map = []
        for r in range(self.rows):
            row = []  # type: List[str]
            for c in range(self.cols):
                row.append("#")
            self.map.append(row)

    def generate(self):
        self.clear()

        firstR = 1 + rand(self.rows - 2)
        firstC = 1 + rand(self.cols - 2)

        self.map[firstR][firstC] = " "
        history = [(firstR, firstC)]
        adjacent = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        diagonals = [(-1, 1), (1, 1), (1, -1), (-1, -1)]

        while len(history):
            r, c = history.pop()
            nextMoves = []  # type: List[Tuple[int, int]]
            for move in adjacent:
                nextR = r + move[0]
                nextC = c + move[1]
                # move is valid if it is in bounds and does not connect to an already open space
                valid = True
                if nextR > 0 and nextR + 1 < self.rows and nextC > 0 and nextC + 1 < self.cols and self.map[nextR][nextC] == "#":
                    # check if any of the spaces adjacent to the prospective move are already open
                    for move2 in adjacent:
                        if nextR + move2[0] == r and nextC + move2[1] == c:
                            continue  # Don't care about the space we're currently at
                        if self.map[nextR + move2[0]][nextC + move2[1]] == " ":
                            valid = False
                        else:
                            for diagonalMove in diagonals:
                                if self.map[nextR + diagonalMove[0]][nextC + diagonalMove[1]] == " " \
                                  and self.map[nextR][nextC + diagonalMove[1]] == "#" \
                                  and self.map[nextR + diagonalMove[0]][nextC] == "#":
                                    valid = False

                else:
                    valid = False  # Out of bounds

                if valid:
                    nextMoves.append((nextR, nextC))

            if len(nextMoves):
                nextR, nextC = pick(nextMoves)
                history.append((r, c))
                self.map[nextR][nextC] = " "
                history.append((nextR, nextC))

    def __str__(self):
        s = ""
        for row in self.map:
            s += "".join(row) + "\n"
        return s


if __name__ == "__main__":
    m = CellDungeon(30, 30)
    m.generate()
    print(m)
