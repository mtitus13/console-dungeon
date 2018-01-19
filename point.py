class Point:
    def __init__(self, r: int, c: int):
        self.r = r
        self.c = c

    def __add__(self, other: "Point") -> "Point":
        return Point(self.r + other.r, self.c + other.c)

    def __str__(self):
        return "(%d,%d)" % (self.r, self.c)

    def __eq__(self, other):
        return self.r == other.r and self.c == other.c

