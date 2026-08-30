# tokens.py

# ---------------------------
# Token types
# ---------------------------
TT_INT      = 'INT'
TT_FLOAT    = 'FLOAT'
TT_STRING   = 'STRING'
TT_IDENT    = 'IDENT'
TT_KEYWORD  = 'SHARD'      # keywords are "shards" of the language

TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_POW      = 'POW'
TT_EQ       = 'EQ'         # =

TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_LBRACE   = 'LBRACE'
TT_RBRACE   = 'RBRACE'

TT_EE       = 'EE'         # ==
TT_NE       = 'NE'         # !=
TT_LT       = 'LT'         # <
TT_GT       = 'GT'         # >
TT_LTE      = 'LTE'        # <=
TT_GTE      = 'GTE'        # >=

TT_COMMA    = 'COMMA'
TT_NEWLINE  = 'NEWLINE'
TT_EOF      = 'EOF'


# ---------------------------
# Obsidian keywords ("shards")
# ---------------------------
KEYWORDS = [
    'forge',    # declare a variable   -> like "let"
    'crack',    # if                   -> a crack forms, branching the flow
    'shatter',  # else                 -> the glass shatters into another path
    'erupt',    # while                -> the loop keeps erupting
    'mold',     # func                 -> molding molten glass into a function
    'cool',     # return               -> lava cools into solid obsidian (final value)
    'solid',    # true                 -> fully cooled = true
    'molten',   # false                -> still molten = not yet true
]


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value is not None:
            return f'{self.type}:{self.value}'
        return f'{self.type}'