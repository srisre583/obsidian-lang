# environment.py

class SymbolTable:
    """
    Holds variable names -> values for a given scope.
    Chains to a parent scope so inner molds (functions) can see
    outer variables, but not vice versa.
    """
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


class Context:
    """
    Tracks *where* code is executing - e.g. inside which mold (function)
    call, and who called it - mainly used for scoping and error tracebacks.
    """
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None