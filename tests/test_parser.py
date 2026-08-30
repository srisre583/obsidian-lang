# test_parser.py

import unittest
from lexer import Lexer
from parser_obsidian import Parser
from ast_nodes import (
    NumberNode, VarAccessNode, VarForgeNode, BinOpNode, UnaryOpNode,
    CrackNode, EruptNode, MoldDefNode, CallNode, CoolNode, ListNode,
)


def parse(source):
    tokens, lex_error = Lexer('<test>', source).tokenize()
    if lex_error:
        return None, lex_error
    ast = Parser(tokens).parse()
    return ast.node, ast.error


class TestParserLiterals(unittest.TestCase):

    def test_number_literal(self):
        node, error = parse('42')
        self.assertIsNone(error)
        self.assertIsInstance(node, ListNode)
        self.assertIsInstance(node.element_nodes[0], NumberNode)
        self.assertEqual(node.element_nodes[0].tok.value, 42)

    def test_variable_access(self):
        node, error = parse('x')
        self.assertIsNone(error)
        self.assertIsInstance(node.element_nodes[0], VarAccessNode)
        self.assertEqual(node.element_nodes[0].var_name_tok.value, 'x')


class TestParserForge(unittest.TestCase):

    def test_forge_declaration(self):
        node, error = parse('forge x = 5')
        self.assertIsNone(error)
        stmt = node.element_nodes[0]
        self.assertIsInstance(stmt, VarForgeNode)
        self.assertEqual(stmt.var_name_tok.value, 'x')
        self.assertIsInstance(stmt.value_node, NumberNode)

    def test_forge_missing_identifier_errors(self):
        node, error = parse('forge = 5')
        self.assertIsNotNone(error)

    def test_forge_missing_equals_errors(self):
        node, error = parse('forge x 5')
        self.assertIsNotNone(error)

    def test_reassignment_existing_variable(self):
        node, error = parse('x = 10')
        self.assertIsNone(error)
        stmt = node.element_nodes[0]
        self.assertIsInstance(stmt, VarForgeNode)
        self.assertEqual(stmt.var_name_tok.value, 'x')


class TestParserOperatorsAndPrecedence(unittest.TestCase):

    def test_simple_addition(self):
        node, error = parse('1 + 2')
        self.assertIsNone(error)
        expr = node.element_nodes[0]
        self.assertIsInstance(expr, BinOpNode)
        self.assertEqual(expr.op_tok.type, 'PLUS')

    def test_multiplication_binds_tighter_than_addition(self):
        # 1 + 2 * 3 should parse as 1 + (2 * 3), i.e. the top node is '+'
        node, error = parse('1 + 2 * 3')
        self.assertIsNone(error)
        expr = node.element_nodes[0]
        self.assertIsInstance(expr, BinOpNode)
        self.assertEqual(expr.op_tok.type, 'PLUS')
        # right side of the '+' should itself be the '*' operation
        self.assertIsInstance(expr.right_node, BinOpNode)
        self.assertEqual(expr.right_node.op_tok.type, 'MUL')

    def test_parentheses_override_precedence(self):
        # (1 + 2) * 3 should parse with '*' at the top
        node, error = parse('(1 + 2) * 3')
        self.assertIsNone(error)
        expr = node.element_nodes[0]
        self.assertEqual(expr.op_tok.type, 'MUL')

    def test_unary_minus(self):
        node, error = parse('-5')
        self.assertIsNone(error)
        expr = node.element_nodes[0]
        self.assertIsInstance(expr, UnaryOpNode)
        self.assertEqual(expr.op_tok.type, 'MINUS')

    def test_comparison_operator(self):
        node, error = parse('x < 10')
        self.assertIsNone(error)
        expr = node.element_nodes[0]
        self.assertIsInstance(expr, BinOpNode)
        self.assertEqual(expr.op_tok.type, 'LT')


class TestParserControlFlow(unittest.TestCase):

    def test_crack_without_shatter(self):
        source = 'crack (x < 10) {\ncool 1\n}'
        node, error = parse(source)
        self.assertIsNone(error)
        stmt = node.element_nodes[0]
        self.assertIsInstance(stmt, CrackNode)
        self.assertEqual(len(stmt.cases), 1)
        self.assertIsNone(stmt.else_case)

    def test_crack_with_shatter(self):
        source = 'crack (x < 10) {\ncool 1\n} shatter {\ncool 2\n}'
        node, error = parse(source)
        self.assertIsNone(error)
        stmt = node.element_nodes[0]
        self.assertIsInstance(stmt, CrackNode)
        self.assertIsNotNone(stmt.else_case)

    def test_crack_missing_paren_errors(self):
        source = 'crack x < 10 {\ncool 1\n}'
        node, error = parse(source)
        self.assertIsNotNone(error)

    def test_erupt_loop(self):
        source = 'erupt (x < 10) {\nx = x + 1\n}'
        node, error = parse(source)
        self.assertIsNone(error)
        stmt = node.element_nodes[0]
        self.assertIsInstance(stmt, EruptNode)


class TestParserFunctions(unittest.TestCase):

    def test_mold_definition_no_args(self):
        source = 'mold greet() {\ncool 1\n}'
        node, error = parse(source)
        self.assertIsNone(error)
        stmt = node.element_nodes[0]
        self.assertIsInstance(stmt, MoldDefNode)
        self.assertEqual(stmt.var_name_tok.value, 'greet')
        self.assertEqual(stmt.arg_name_toks, [])

    def test_mold_definition_with_args(self):
        source = 'mold add(a, b) {\ncool a + b\n}'
        node, error = parse(source)
        self.assertIsNone(error)
        stmt = node.element_nodes[0]
        self.assertIsInstance(stmt, MoldDefNode)
        arg_names = [t.value for t in stmt.arg_name_toks]
        self.assertEqual(arg_names, ['a', 'b'])

    def test_function_call_no_args(self):
        node, error = parse('greet()')
        self.assertIsNone(error)
        stmt = node.element_nodes[0]
        self.assertIsInstance(stmt, CallNode)
        self.assertEqual(len(stmt.arg_nodes), 0)

    def test_function_call_with_args(self):
        node, error = parse('add(1, 2)')
        self.assertIsNone(error)
        stmt = node.element_nodes[0]
        self.assertIsInstance(stmt, CallNode)
        self.assertEqual(len(stmt.arg_nodes), 2)

    def test_cool_with_value(self):
        node, error = parse('cool 42')
        self.assertIsNone(error)
        stmt = node.element_nodes[0]
        self.assertIsInstance(stmt, CoolNode)
        self.assertIsInstance(stmt.node_to_return, NumberNode)

    def test_cool_without_value(self):
        node, error = parse('cool')
        self.assertIsNone(error)
        stmt = node.element_nodes[0]
        self.assertIsInstance(stmt, CoolNode)
        self.assertIsNone(stmt.node_to_return)


class TestParserMultiStatement(unittest.TestCase):

    def test_multiple_statements_separated_by_newline(self):
        source = 'forge x = 1\nforge y = 2\nx + y'
        node, error = parse(source)
        self.assertIsNone(error)
        self.assertEqual(len(node.element_nodes), 3)

    def test_full_program_parses_without_error(self):
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
        node, error = parse(source)
        self.assertIsNone(error)
        self.assertEqual(len(node.element_nodes), 4)


if __name__ == '__main__':
    unittest.main()