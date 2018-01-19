class Feature:
    def __init__(self):
        self.glyph = ""
        self.type = "unknown"


class DownStairs(Feature):
    def __init__(self):
        self.glyph = ">"
        self.type = "downstairs"


class UpStairs(Feature):
    def __init__(self):
        self.glyph = "<"
        self.type = "upstairs"
