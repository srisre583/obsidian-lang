# test_interpreter.py

import unittest
from lexer import Lexer
from parser_obsidian import Parser
from interpreter import Interpreter
from environment import Context, SymbolTable
from builtins import install_builtins


def run_program(source):
    """
    Runs a full Obsidian program end-to-end and returns (result, error).
    Each call gets a fresh global scope, so tests don't leak state into each other.
    """
    tokens, lex_error = Lexer('<test>', source).tokenize()
    if lex_error:
        return None, lex_error

    ast = Parser(tokens).parse()
    if ast.error:
        return None, ast.error

    symbol_table = SymbolTable()
    install_builtins(symbol_table)

    context = Context('<program>')
    context.symbol_table = symbol_table

    result = Interpreter().visit(ast.node, context)
    if result.error:
        return None, result.error

    final = result.func_return_value if result.func_return_value is not None else result.value
    return final, None


def value_of(result):
    """Unwraps a Number value into a plain Python number for easy assertions."""
    return result.value if result is not None else None


class TestInterpreterArithmetic(unittest.TestCase):

    def test_addition(self):
        result, error = run_program('2 + 3')
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 5)

    def test_operator_precedence(self):
        result, error = run_program('2 + 3 * 4')
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 14)

    def test_division(self):
        result, error = run_program('10 / 4')
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 2.5)

    def test_division_by_zero_errors(self):
        result, error = run_program('5 / 0')
        self.assertIsNotNone(error)
        self.assertIn('Division by zero', error.details)

    def test_power(self):
        result, error = run_program('2 ^ 5')
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 32)

    def test_unary_minus(self):
        result, error = run_program('-5 + 10')
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 5)


class TestInterpreterVariables(unittest.TestCase):

    def test_forge_and_access(self):
        result, error = run_program('forge x = 5\nx + 1')
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 6)

    def test_reassignment(self):
        result, error = run_program('forge x = 5\nx = x + 1\nx')
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 6)

    def test_undefined_variable_errors(self):
        result, error = run_program('y + 1')
        self.assertIsNotNone(error)
        self.assertIn('not defined', error.details)


class TestInterpreterBooleans(unittest.TestCase):

    def test_solid_is_one(self):
        result, error = run_program('solid')
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 1)

    def test_molten_is_zero(self):
        result, error = run_program('molten')
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 0)

    def test_comparison_true(self):
        result, error = run_program('5 < 10')
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 1)

    def test_comparison_false(self):
        result, error = run_program('5 > 10')
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 0)


class TestInterpreterControlFlow(unittest.TestCase):

    def test_crack_true_branch(self):
        source = 'crack (5 < 10) {\ncool 1\n} shatter {\ncool 2\n}'
        result, error = run_program(source)
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 1)

    def test_crack_false_branch(self):
        source = 'crack (5 > 10) {\ncool 1\n} shatter {\ncool 2\n}'
        result, error = run_program(source)
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 2)

    def test_erupt_loop_counts_up(self):
        source = 'forge x = 0\nerupt (x < 5) {\nx = x + 1\n}\nx'
        result, error = run_program(source)
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 5)


class TestInterpreterFunctions(unittest.TestCase):

    def test_function_call(self):
        source = 'mold add(a, b) {\ncool a + b\n}\nadd(2, 3)'
        result, error = run_program(source)
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 5)

    def test_recursion(self):
        source = '''
mold fact(n) {
    crack (n < 2) {
        cool 1
    } shatter {
        cool n * fact(n - 1)
    }
}
fact(5)
'''
        result, error = run_program(source)
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 120)

    def test_too_few_args_errors(self):
        source = 'mold add(a, b) {\ncool a + b\n}\nadd(1)'
        result, error = run_program(source)
        self.assertIsNotNone(error)
        self.assertIn('too few args', error.details)

    def test_too_many_args_errors(self):
        source = 'mold add(a, b) {\ncool a + b\n}\nadd(1, 2, 3)'
        result, error = run_program(source)
        self.assertIsNotNone(error)
        self.assertIn('too many args', error.details)


class TestInterpreterFullProgram(unittest.TestCase):

    def test_combined_program(self):
        source = '''
mold add(a, b) {
    cool a + b
}

forge total = add(2, 3)

erupt (total < 20) {
    total = total + 1
}

crack (total > 15) {
    cool total
} shatter {
    cool 0
}
'''
        result, error = run_program(source)
        self.assertIsNone(error)
        self.assertEqual(value_of(result), 20)


if __name__ == '__main__':
    unittest.main()