# test_lexer.py

import unittest
from lexer import Lexer
from tokens import (
    TT_INT, TT_FLOAT, TT_IDENT, TT_KEYWORD,
    TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_POW, TT_EQ,
    TT_LPAREN, TT_RPAREN, TT_LBRACE, TT_RBRACE,
    TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE,
    TT_COMMA, TT_NEWLINE, TT_EOF,
)


def tokenize(source):
    tokens, error = Lexer('<test>', source).tokenize()
    return tokens, error


class TestLexerNumbers(unittest.TestCase):

    def test_integer(self):
        tokens, error = tokenize('42')
        self.assertIsNone(error)
        self.assertEqual(tokens[0].type, TT_INT)
        self.assertEqual(tokens[0].value, 42)

    def test_float(self):
        tokens, error = tokenize('3.14')
        self.assertIsNone(error)
        self.assertEqual(tokens[0].type, TT_FLOAT)
        self.assertAlmostEqual(tokens[0].value, 3.14)

    def test_multiple_numbers(self):
        tokens, error = tokenize('1 2 3')
        self.assertIsNone(error)
        values = [t.value for t in tokens if t.type == TT_INT]
        self.assertEqual(values, [1, 2, 3])


class TestLexerIdentifiersAndKeywords(unittest.TestCase):

    def test_identifier(self):
        tokens, error = tokenize('myVar')
        self.assertIsNone(error)
        self.assertEqual(tokens[0].type, TT_IDENT)
        self.assertEqual(tokens[0].value, 'myVar')

    def test_keyword_forge(self):
        tokens, error = tokenize('forge')
        self.assertIsNone(error)
        self.assertEqual(tokens[0].type, TT_KEYWORD)
        self.assertEqual(tokens[0].value, 'forge')

    def test_all_obsidian_keywords_recognized(self):
        keywords = ['forge', 'crack', 'shatter', 'erupt', 'mold', 'cool', 'solid', 'molten']
        for kw in keywords:
            tokens, error = tokenize(kw)
            self.assertIsNone(error)
            self.assertEqual(tokens[0].type, TT_KEYWORD, f'{kw} should be a keyword')

    def test_identifier_not_confused_with_keyword(self):
        # 'forgery' contains 'forge' but should NOT be tokenized as the keyword
        tokens, error = tokenize('forgery')
        self.assertIsNone(error)
        self.assertEqual(tokens[0].type, TT_IDENT)
        self.assertEqual(tokens[0].value, 'forgery')


class TestLexerOperators(unittest.TestCase):

    def test_arithmetic_operators(self):
        tokens, error = tokenize('+ - * / ^')
        self.assertIsNone(error)
        types = [t.type for t in tokens if t.type != TT_EOF]
        self.assertEqual(types, [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_POW])

    def test_single_equals(self):
        tokens, error = tokenize('=')
        self.assertIsNone(error)
        self.assertEqual(tokens[0].type, TT_EQ)

    def test_double_equals(self):
        tokens, error = tokenize('==')
        self.assertIsNone(error)
        self.assertEqual(tokens[0].type, TT_EE)

    def test_not_equals(self):
        tokens, error = tokenize('!=')
        self.assertIsNone(error)
        self.assertEqual(tokens[0].type, TT_NE)

    def test_comparison_operators(self):
        tokens, error = tokenize('< > <= >=')
        self.assertIsNone(error)
        types = [t.type for t in tokens if t.type != TT_EOF]
        self.assertEqual(types, [TT_LT, TT_GT, TT_LTE, TT_GTE])

    def test_illegal_character_after_bang(self):
        # '!' must be followed by '=' in Obsidian; '!' alone is invalid
        tokens, error = tokenize('!5')
        self.assertIsNotNone(error)


class TestLexerPunctuation(unittest.TestCase):

    def test_parens_and_braces(self):
        tokens, error = tokenize('(){}')
        self.assertIsNone(error)
        types = [t.type for t in tokens if t.type != TT_EOF]
        self.assertEqual(types, [TT_LPAREN, TT_RPAREN, TT_LBRACE, TT_RBRACE])

    def test_comma(self):
        tokens, error = tokenize(',')
        self.assertIsNone(error)
        self.assertEqual(tokens[0].type, TT_COMMA)

    def test_newline_token(self):
        tokens, error = tokenize('1\n2')
        self.assertIsNone(error)
        types = [t.type for t in tokens if t.type != TT_EOF]
        self.assertEqual(types, [TT_INT, TT_NEWLINE, TT_INT])

    def test_semicolon_as_newline(self):
        tokens, error = tokenize('1;2')
        self.assertIsNone(error)
        types = [t.type for t in tokens if t.type != TT_EOF]
        self.assertEqual(types, [TT_INT, TT_NEWLINE, TT_INT])


class TestLexerComments(unittest.TestCase):

    def test_comment_is_ignored(self):
        tokens, error = tokenize('5 # this is a comment\n6')
        self.assertIsNone(error)
        values = [t.value for t in tokens if t.type == TT_INT]
        self.assertEqual(values, [5, 6])


class TestLexerErrors(unittest.TestCase):

    def test_illegal_character(self):
        tokens, error = tokenize('@')
        self.assertIsNotNone(error)
        self.assertEqual(error.error_name, 'Illegal Character')

    def test_eof_always_present(self):
        tokens, error = tokenize('')
        self.assertIsNone(error)
        self.assertEqual(tokens[-1].type, TT_EOF)


class TestLexerFullProgram(unittest.TestCase):

    def test_forge_statement(self):
        tokens, error = tokenize('forge x = 5 + 3')
        self.assertIsNone(error)
        types = [t.type for t in tokens if t.type != TT_EOF]
        self.assertEqual(types, [
            TT_KEYWORD, TT_IDENT, TT_EQ, TT_INT, TT_PLUS, TT_INT
        ])

    def test_crack_shatter_block(self):
        source = 'crack (x < 10) {\ncool solid\n} shatter {\ncool molten\n}'
        tokens, error = tokenize(source)
        self.assertIsNone(error)
        keyword_values = [t.value for t in tokens if t.type == TT_KEYWORD]
        self.assertEqual(keyword_values, ['crack', 'cool', 'solid', 'shatter', 'cool', 'molten'])


if __name__ == '__main__':
    unittest.main()