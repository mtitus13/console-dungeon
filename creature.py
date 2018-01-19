class Creature:
    def __init__(self):
        self.hp = 0
        self.maxhp = 0
        self.name = ""
        self.glyph = ""
        self.waitTime = 0
        self.speed = 0
        self.player = False


class Player(Creature):
    def __init__(self):
        Creature.__init__(self)
        self.glyph = "@"
        self.speed = 10
        self.player = True
