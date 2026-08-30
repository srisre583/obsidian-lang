# main.py

import sys
import os

# main.py lives inside a scripts/ folder, but the language modules
# (lexer.py, parser_obsidian.py, etc.) might be one or two folders up,
# depending on how the project is nested. Search nearby folders for
# lexer.py and add whichever one actually contains it to the import path.
_here = os.path.dirname(os.path.abspath(__file__))
_candidates = [
    _here,
    os.path.dirname(_here),                                  # one level up
    os.path.join(os.path.dirname(_here), 'obsidian'),         # sibling 'obsidian' folder
    os.path.dirname(os.path.dirname(_here)),                  # two levels up
]

_found = False
for _candidate in _candidates:
    if os.path.isfile(os.path.join(_candidate, 'lexer.py')):
        if _candidate not in sys.path:
            sys.path.insert(0, _candidate)
        _found = True
        break

if not _found:
    print("Could not find lexer.py in any nearby folder. Looked in:")
    for _candidate in _candidates:
        print(f"  - {_candidate}")
    print("Edit the _candidates list in main.py to point at the correct folder.")
    sys.exit(1)

from lexer import Lexer
from parser_obsidian import Parser
from interpreter import Interpreter
from environment import Context, SymbolTable
from builtins_obsidian import install_builtins
from values import Null

# .obs scripts live in the same folder as this file
SCRIPTS_DIR = _here

# Global scope for the running script
global_symbol_table = SymbolTable()
install_builtins(global_symbol_table)


def resolve_script_path(filename):
    """
    Figures out the actual path to a .obs file:
    - If the given path already exists as-is (e.g. a full path, or a
      relative path from the current directory), use it directly.
    - Otherwise, look for it inside the scripts/ folder next to main.py.
    """
    if os.path.isfile(filename):
        return filename

    candidate = os.path.join(SCRIPTS_DIR, filename)
    if os.path.isfile(candidate):
        return candidate

    # Nothing found — return the scripts/ candidate so the error message
    # shown to the user points at where we actually looked.
    return candidate


def run(fn, text):
    tokens, error = Lexer(fn, text).tokenize()
    if error:
        return None, error

    ast = Parser(tokens).parse()
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


def run_file(path):
    resolved_path = resolve_script_path(path)

    try:
        with open(resolved_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file '{path}' not found (looked in '.' and '{SCRIPTS_DIR}')")
        sys.exit(1)

    result, error = run(resolved_path, source)

    if error:
        print(error.as_string())
        sys.exit(1)

    # Only print the final result if it's a real value (not Null/void)
    if result is not None and not isinstance(result, Null):
        print(result)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <filename>.obs")
        sys.exit(1)

    run_file(sys.argv[1])