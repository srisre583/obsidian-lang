# repl.py

from lexer import Lexer
from parser_obsidian import Parser
from interpreter import Interpreter
from environment import Context, SymbolTable
from builtins_obsidian import install_builtins
from values import Null

# Global scope shared across the whole REPL session
global_symbol_table = SymbolTable()
install_builtins(global_symbol_table)


def run(fn, text):
    tokens, error = Lexer(fn, text).tokenize()
    if error:
        return None, error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table

    result = interpreter.visit(ast.node, context)
    if result.error:
        return None, result.error

    final = result.func_return_value if result.func_return_value is not None else result.value
    return final, None


def needs_more_input(text):
    """
    Returns True if braces are unbalanced, meaning the user is still
    in the middle of typing a mold/crack/erupt block and the REPL
    should keep collecting lines instead of running yet.
    """
    return text.count('{') > text.count('}')


def main():
    print("Obsidian REPL — type 'exit' to quit")
    print(f"({__name__} session)\n")

    while True:
        try:
            text = input('obsidian > ')
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if text.strip() == '':
            continue
        if text.strip() == 'exit':
            break

        # Keep reading lines until braces balance out, so multi-line
        # mold/crack/erupt blocks can be typed naturally.
        full_input = text
        while needs_more_input(full_input):
            try:
                line = input('        ... ')
            except (EOFError, KeyboardInterrupt):
                print()
                full_input = ''
                break
            full_input += '\n' + line

        if full_input.strip() == '':
            continue

        result, error = run('<stdin>', full_input)

        if error:
            print(error.as_string())
        elif result is not None and not isinstance(result, Null):
            print(result)


if __name__ == '__main__':
    main()