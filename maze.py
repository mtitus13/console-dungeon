from typing import List, Dict, Union
from point import Point
import feature
from rand import rand, pick
from creature import Creature


class Room:
    directions = ('north', 'east', 'south', 'west')
    oppositeDirections = {'north': 'south', 'east': 'west', 'south': 'north', 'west': 'east'}
    moves = {'north': Point(-1, 0), 'east': Point(0, 1), 'south': Point(1, 0), 'west': Point(0, -1)}  # type:  Dict[str, Point]

    def __init__(self):
        self.exits = {}  # type: Dict[str, bool]
        for d in Room.directions:
            self.exits[d] = False

        self.zone = -1
        self.feature = None  # type: feature.Feature
        self.creature = None  # type: Creature

    def glyph(self) -> str:
        glyph = " "

        if self.creature:
            glyph = self.creature.glyph
        elif self.feature:
            glyph = self.feature.glyph

        return glyph

    def numExits(self) -> int:
        numExits = 0
        for direction in Room.directions:
            if self.exits[direction]:
                numExits += 1
        return numExits


class Tunneler:
    def __init__(self):
        self.history = []  # type: List[Point]
        self.zone = 0


class Maze:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.offset_row = 0
        self.offset_col = 0

        self.map = []  # type: List[List[Union[Room,None]]]

    def clear(self):
        self.map = []
        for r in range(self.rows):
            row = []  # type: List[Union[Room, None]]
            for c in range(self.cols):
                row.append(None)
            self.map.append(row)

    def getRoom(self, p: Point) -> Union[Room, None]:
        if not self.validPoint(p):
            return None
        if self.map[p.r][p.c] is None:
            self.map[p.r][p.c] = Room()
        return self.map[p.r][p.c]

    def validPoint(self, p: Point) -> bool:
        if p.r < 0 or p.r >= len(self.map):
            return False
        if p.c < 0 or p.c >= len(self.map[p.r]):
            return False
        return True

    def generate(self, upstairs: List[Point] = None) -> List[Point]:
        if upstairs is None:
            upstairs = []

        downstairs = []

        self.clear()

        numTunnelers = 1
        tunnelers = []  # type: List[Tunneler]
        tunneler = Tunneler()
        start = Point(rand(self.rows), rand(self.cols))
        tunneler.history.append(start)
        self.getRoom(start).zone = 0
        tunnelers.append(tunneler)

        while len(tunnelers):
            for t in range(len(tunnelers)):
                if t >= len(tunnelers): break
                tunneler = tunnelers[t]
                r = tunneler.history[-1]
                nextrooms = []  # type: List[str]
                for d, p in Room.moves.items():
                    r2 = r + p
                    if self.validPoint(r2) and self.getRoom(r2).zone == -1:
                        nextrooms.append(d)

                if len(nextrooms):
                    x = rand(len(nextrooms))
                    d = nextrooms[x]
                    r2 = r + Room.moves[d]
                    self.getRoom(r).exits[d] = True
                    self.getRoom(r2).exits[Room.oppositeDirections[d]] = True
                    self.getRoom(r2).zone = tunneler.zone
                    tunneler.history.append(r2)
                else:
                    tunneler.history.pop()
                    if len(tunneler.history) == 0:
                        del tunnelers[t]

            if len(tunnelers) and rand(15) == 0:
                tunneler = Tunneler()
                tunneler.zone = numTunnelers
                numTunnelers += 1
                rooms = []  # type: List[Point]
                for r in range(len(self.map)):
                    for c in range(len(self.map[r])):
                        p = Point(r, c)
                        if self.getRoom(p).zone == -1:
                            rooms.append(p)
                if len(rooms):
                    p2 = pick(rooms)
                    tunneler.history.append(p2)
                    self.getRoom(p2).zone = tunneler.zone
                    tunnelers.append(tunneler)

        # out_rooms = []  # type: List[Point]
        # for r in range(len(self.map)):
        #     for c in range(len(self.map[r])):
        #         out_rooms.append(Point(r, c))
        #
        # next_zone = [0]
        # in_rooms = []  # type: List[Point]
        # next_rooms = []  # type: List[Point]
        #
        # def startNewZone():
        #     if len(out_rooms) == 0:
        #         return
        #
        #     first_room = pick(out_rooms)
        #     out_rooms.remove(first_room)
        #     room = self.getRoom(first_room)
        #     room.zone = next_zone[0]
        #     next_zone[0] += 1
        #     in_rooms.append(first_room)
        #
        #     for direction, delta in Room.moves.items():
        #         room2 = first_room + delta
        #         if room2 in out_rooms:
        #             out_rooms.remove(room2)
        #             next_rooms.append(room2)
        #
        # startNewZone()
        #
        # while len(next_rooms):
        #     next_room = pick(next_rooms)
        #     next_rooms.remove(next_room)
        #     if next_room not in in_rooms:
        #         moves = []  # type: List[str]
        #         for direction, delta in Room.moves.items():
        #             room2 = next_room + delta
        #             if room2 in in_rooms:
        #                 moves.append(direction)
        #
        #         if len(moves):
        #             next_dir = pick(moves)
        #             room = self.getRoom(next_room)
        #             room2_pos = next_room + Room.moves[next_dir]
        #             room2 = self.getRoom(room2_pos)
        #             room.zone = room2.zone
        #             room.exits[next_dir] = True
        #             room2.exits[Room.oppositeDirections[next_dir]] = True
        #             in_rooms.append(next_room)
        #
        #             for direction, delta in Room.moves.items():
        #                 room2 = next_room + delta
        #                 if self.validPoint(room2) and room2 in out_rooms:
        #                     next_rooms.append(room2)
        #                     out_rooms.remove(room2)
        #     if rand(100) < 1:
        #         startNewZone()

        print(self)
        self.generate_rollbackDeadends()

        for p in upstairs:
            self.getRoom(p).feature = feature.UpStairs()
            self.getRoom(p).exits["up"] = True

        zoneRooms = []  # type: List[List[Point]]
        for r in range(len(self.map)):
            for c in range(len(self.map[r])):
                room = self.map[r][c]
                if room is not None:
                    while room.zone >= len(zoneRooms):
                        zoneRooms.append([])
                    zoneRooms[room.zone].append(Point(r, c))

        for zone in zoneRooms:
            if len(zone):
                p = pick(zone)
                while self.getRoom(p).feature is not None:
                    p = pick(zone)
                self.getRoom(p).feature = feature.DownStairs()
                self.getRoom(p).exits["down"] = True
                downstairs.append(p)

        return downstairs

    def generate_rollbackDeadends(self):
        deadends = []  # type: List[Point]
        stopRooms = []  # type: List[Point]
        for r in range(len(self.map)):
            for c in range(len(self.map[r])):
                p = Point(r, c)
                if self.getRoom(p) is not None and self.getRoom(p).numExits() == 1:
                    deadends.append(p)
                if self.getRoom(p) is not None and self.getRoom(p).numExits() > 2 or self.getRoom(p).feature is not None:
                    stopRooms.append(p)

        while len(deadends):
            room = deadends.pop()
            if room not in stopRooms:
                exit = ""
                for direction, open in self.getRoom(room).exits.items():
                    if open:
                        exit = direction

                if exit != "":
                    nextRoom = room + Room.moves[exit]
                    self.getRoom(nextRoom).exits[Room.oppositeDirections[exit]] = False
                    deadends.insert(0, nextRoom)

                self.setRoom(room, None)

        for r in range(len(self.map)):
            for c in range(len(self.map[r])):
                p = Point(r,c)
                if self.getRoom(p) is not None and self.getRoom(p).numExits() == 0:
                    self.setRoom(p, None)


# def generate

    def __str__(self) -> str:
        chrs = []  # type: List[List[str]]
        for x in range(self.rows):
            for z in range(2):
                line = [' ']  # type: List[str]
                for y in range(self.cols):
                    line.append(' ')
                    line.append(' ')
                chrs.append(line)
        chrs.append([' '] * (self.cols * 2 + 1))

        r = 0
        for x in range(self.rows):
            c = 0
            for y in range(self.cols):
                room = self.map[x][y]
                if room:
                    chrs[r][c] = "#"
                    c += 1
                    if not room.exits['north']:
                        chrs[r][c] = "#"
                    c += 1
                    chrs[r][c] = "#"
                else:
                    c += 2
            r += 1
            c = 0
            for y in range(self.cols):
                room = self.map[x][y]
                if room:
                    if not room.exits['west']:
                        chrs[r][c] = "#"
                    c += 1
                    chrs[r][c] = room.glyph()
                    c += 1
                    if not room.exits['east']:
                        chrs[r][c] = "#"
                else:
                    c += 2
            r += 1
            c = 0
            for y in range(self.cols):
                room = self.map[x][y]
                if room:
                    chrs[r][c] = "#"
                    c += 1
                    if not room.exits['south']:
                        chrs[r][c] = "#"
                    c += 1
                    chrs[r][c] = "#"
                else:
                    c += 2

        # Trim blank rows at the top
        abort = False
        while not abort:
            row = chrs[0]
            for char in row:
                if char != " ":
                    abort = True
                    break
                if abort:
                    break
            if not abort:
                del(chrs[0])

        # Trim blank rows from the bottom
        abort = False
        while not abort:
            row = chrs[-1]
            for char in row:
                if char != " ":
                    abort = True
                    break
                if abort:
                    break
            if not abort:
                del(chrs[-1])

        # Trim blank columns at the left
        abort = False
        while not abort:
            for r in chrs:
                if r[0] != " ":
                    abort = True
                    break
                if abort:
                    break
            if not abort:
                for r in chrs:
                    del(r[0])

        # Add one blank row and column for spacing
        chrs.insert(0, [' '] * len(chrs[0]))
        for r in chrs:
            r.insert(0, ' ')

        return "\n".join(map(lambda r: "".join(r), chrs))

    def setRoom(self, pos: Point, room: Union[Room, None]):
        row, col = (pos.r, pos.c)
        row += self.offset_row
        col += self.offset_col
        while row < 0:
            self.rows += 1
            self.offset_row += 1
            row += 1
            self.map.insert(0, [None] * self.cols)
        while col < 0:
            self.cols += 1
            self.offset_col += 1
            col += 1
            for r in self.map:
                r.insert(0, None)

        while row >= self.rows:
            self.rows += 1
            self.map.append([None] * self.cols)

        while col >= self.cols:
            self.cols += 1
            for r in self.map:
                r.append(None)

        self.map[row][col] = room


if __name__ == "__main__":
    m = Maze(50, 50)
    m.generate()
    print(m)
