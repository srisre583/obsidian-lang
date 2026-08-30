"""
Obsidian - a programming language implemented in Python.
"""

__version__ = "0.1.0"

from .lexer import Lexer
from .parser_obsidian import Parser
from .interpreter import Interpreter
from .errors import ObsidianError, ObsidianSyntaxError, ObsidianRuntimeError

__all__ = [
    "Lexer",
    "Parser",
    "Interpreter"
    "ObsidianError",
    "ObsidianSyntaxError",
    "ObsidianRuntimeError",
    "run",
    "run_file",
]

def run(source: str):
    """Run Obsidian source code from a string and return the result."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    return Interpreter().interpret(ast)

def run_file(path: str):
    """Run an Obsidian (.obs) source file."""
    with open (path, "r", encoding="utf-8") as f:
        source = f.read()
    return run(source)