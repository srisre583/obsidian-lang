# Obsidian 🖤🌋

Obsidian is a small interpreted programming language, built from scratch in Python. It has its own lexer, parser, and tree-walking interpreter — no external parsing libraries involved.

The language's keywords are themed around volcanic glass and lava, since molten rock cools into obsidian: variables are **forged**, functions are **molded**, conditionals **crack**, loops **erupt**, and values **cool** back out.

## Features

- Variables (`forge`, reassignment)
- Numbers (integers and floats) and strings
- Arithmetic (`+ - * / ^`) and comparisons (`< > <= >= == !=`)
- Booleans (`solid` / `molten`)
- Conditionals (`crack` / `shatter`)
- Loops (`erupt`)
- Functions (`mold`), function calls, recursion, and return values (`cool`)
- Built-in functions: `speak`, `listen`, `solid_check`, `clear`
- A REPL and a script runner
- A test suite covering the lexer, parser, and interpreter

## Example

```obsidian
mold fact(n) {
    crack (n < 2) {
        cool 1
    } shatter {
        cool n * fact(n - 1)
    }
}

forge result = fact(6)
speak(result)
```

```
720
```

## Getting started

### Requirements

- Python 3.8+

### Run the REPL

```bash
python3 repl.py
```

```
Obsidian REPL — type 'exit' to quit
obsidian > forge x = 5
obsidian > speak(x + 10)
15
```

The REPL supports multi-line blocks — if you open a `{`, it keeps prompting with `...` until the block is closed:

```
obsidian > mold add(a, b) {
        ... cool a + b
        ... }
obsidian > speak(add(2, 3))
5
```

### Run a script file

Write a `.obs` file:

```obsidian
speak("Hello, Obsidian!")
```

Then run it:

```bash
python3 main.py hello_world.obs
```

```
Hello, Obsidian!
```

## Language reference

| Obsidian keyword | Meaning              | Equivalent in most languages |
|-------------------|-----------------------|-------------------------------|
| `forge`           | declare a variable     | `let` / `var`                |
| `crack`           | if                     | `if`                          |
| `shatter`         | else                   | `else`                        |
| `erupt`           | while loop             | `while`                       |
| `mold`            | define a function      | `func` / `def`                |
| `cool`            | return a value         | `return`                      |
| `solid`           | boolean true           | `true`                        |
| `molten`          | boolean false          | `false`                       |

### Built-in functions

| Function              | Description                                      |
|------------------------|--------------------------------------------------|
| `speak(value)`         | prints a value to the console                    |
| `listen()`             | reads a line of input as a number                |
| `solid_check(value)`   | returns `solid` if `value` is truthy, else `molten` |
| `clear()`              | clears the terminal screen                       |

### Comments

```obsidian
# this is a comment
forge x = 5  # comments can trail a line too
```

### Strings

```obsidian
forge name = "world"
speak("hello " + name)   # concatenation
speak("ab" * 3)           # repetition -> "ababab"
```

> Note: strings and numbers don't automatically mix — `"count: " + 5` will raise an error, since `5` is a number, not a string.

## Project structure

```
obsidian/
├── tokens.py              # token type definitions and the Token class
├── position.py            # tracks line/column for error messages
├── errors.py               # error classes (syntax, runtime, illegal character)
├── lexer.py                 # turns source text into tokens
├── ast_nodes.py             # AST node classes
├── parser_obsidian.py       # recursive descent parser (tokens -> AST)
├── values.py                 # runtime value types (Number, String, Function, Null)
├── environment.py            # variable scoping (SymbolTable, Context)
├── interpreter.py            # walks the AST and executes it
├── builtins_obsidian.py      # native functions callable from Obsidian (speak, listen, ...)
├── repl.py                    # interactive shell with multi-line block support
├── shell.py                   # simpler interactive shell
├── main.py                     # runs a .obs script file
├── __init__.py                  # package entry point (run / run_file)
├── test_lexer.py                # lexer unit tests
├── test_parser.py               # parser unit tests
└── test_interpreter.py          # interpreter (end-to-end) unit tests
```

## Running the tests

```bash
python3 -m unittest discover -p "test_*.py" -v
```

## Roadmap / ideas

- [ ] Lists / arrays
- [ ] String/number interop (e.g. a `str_of()` conversion built-in)
- [ ] `not` / `and` / `or` boolean keyword support in the lexer's `KEYWORDS` list
- [ ] File I/O built-ins
- [ ] Better error recovery in the parser (currently stops at the first error)