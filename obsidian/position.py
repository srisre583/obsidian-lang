# position.py

class Position:
    def __init__(self, idx, line, col, fn, ftxt):
        self.idx = idx      # index into the source string
        self.line = line
        self.col = col
        self.fn = fn        # filename
        self.ftxt = ftxt    # full source text

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.line += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.line, self.col, self.fn, self.ftxt)