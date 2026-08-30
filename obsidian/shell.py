# shell.py

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

    # A top-level 'cool' sets func_return_value rather than value
    final = result.func_return_value if result.func_return_value is not None else result.value
    return final, None


if __name__ == '__main__':
    print("Obsidian REPL — type 'exit' to quit")
    while True:
        text = input('obsidian > ')
        if text.strip() == '':
            continue
        if text.strip() == 'exit':
            break

        result, error = run('<stdin>', text)

        if error:
            print(error.as_string())
        elif result is not None and not isinstance(result, Null):
            print(result)