# builtins_obsidian.py

from values import Value, Number, Null
from errors import ObsidianRuntimeError


class BuiltInFunction(Value):
    """
    A function implemented in Python rather than in Obsidian itself.
    Examples: speak (print), listen (input), solidify (to-string), etc.
    """
    def __init__(self, name):
        super().__init__()
        self.name = name

    def execute(self, args):
        # Local import avoids a circular import with interpreter.py
        from interpreter import RTResult
        from environment import Context, SymbolTable

        res = RTResult()
        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_execute_method)

        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(self.context.symbol_table if self.context else None)

        arg_names = method.arg_names

        if len(args) > len(arg_names):
            return res.failure(ObsidianRuntimeError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into '{self.name}'",
                self.context
            ))

        if len(args) < len(arg_names):
            return res.failure(ObsidianRuntimeError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} too few args passed into '{self.name}'",
                self.context
            ))

        for i, arg_value in enumerate(args):
            arg_value.set_context(new_context)
            new_context.symbol_table.set(arg_names[i], arg_value)

        return_value = res.register(method(new_context))
        if res.error:
            return res

        return res.success(return_value)

    def no_execute_method(self, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f'<built-in mold {self.name}>'

    # ---------------------------
    # Built-in implementations
    # ---------------------------

    def execute_speak(self, context):
        """speak(value) — prints a value to the console."""
        from interpreter import RTResult
        value = context.symbol_table.get('value')
        print(str(value))
        return RTResult().success(Null.nothing)
    execute_speak.arg_names = ['value']

    def execute_listen(self, context):
        """listen() — reads a line of input from the user as a Number (if possible)."""
        from interpreter import RTResult
        text = input()
        try:
            value = Number(int(text))
        except ValueError:
            try:
                value = Number(float(text))
            except ValueError:
                value = Number(0)
        return RTResult().success(value)
    execute_listen.arg_names = []

    def execute_solid_check(self, context):
        """solid_check(value) — returns solid(1) if value is truthy, else molten(0)."""
        from interpreter import RTResult
        value = context.symbol_table.get('value')
        result = Number.solid if value.is_true() else Number.molten
        return RTResult().success(result)
    execute_solid_check.arg_names = ['value']

    def execute_clear(self, context):
        """clear() — clears the terminal screen."""
        from interpreter import RTResult
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        return RTResult().success(Null.nothing)
    execute_clear.arg_names = []


# Pre-instantiated built-ins, ready to be registered into a symbol table
BuiltInFunction.speak = BuiltInFunction('speak')
BuiltInFunction.listen = BuiltInFunction('listen')
BuiltInFunction.solid_check = BuiltInFunction('solid_check')
BuiltInFunction.clear = BuiltInFunction('clear')


def install_builtins(symbol_table):
    """
    Registers all built-in functions and constants into the given symbol table.
    Call this once on your global scope before running any Obsidian code.
    """
    symbol_table.set('speak', BuiltInFunction.speak)
    symbol_table.set('listen', BuiltInFunction.listen)
    symbol_table.set('solid_check', BuiltInFunction.solid_check)
    symbol_table.set('clear', BuiltInFunction.clear)
    symbol_table.set('solid', Number.solid)
    symbol_table.set('molten', Number.molten)