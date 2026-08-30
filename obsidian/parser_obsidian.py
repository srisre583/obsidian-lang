# parser_obsidian.py

from tokens import *
from ast_nodes import *
from errors import ObsidianSyntaxError


class ParseResult:
    """Wraps a parsing outcome: either a successful node, or an error."""
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.statements()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '+', '-', '*', '/' or end of input"
            ))
        return res

    # ---------------------------
    # Grammar rules
    # ---------------------------

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement(); self.advance()

        statement = res.register(self.statement())
        if res.error:
            return res
        statements.append(statement)

        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement(); self.advance()
                newline_count += 1

            # No newline separator means this run of statements is done
            if newline_count == 0:
                break

            # End of a block or end of input also ends the statement list
            if self.current_tok.type in (TT_RBRACE, TT_EOF):
                break

            statement = res.register(self.statement())
            if res.error:
                return res
            statements.append(statement)

        return res.success(ListNode(statements, pos_start, self.current_tok.pos_end.copy()))

    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.matches(TT_KEYWORD, 'cool'):
            res.register_advancement(); self.advance()

            expr_node = None
            # 'cool' can optionally be followed by a value, e.g. `cool x + 1`
            if self.current_tok.type not in (TT_NEWLINE, TT_EOF, TT_RBRACE):
                expr_node = res.register(self.expr())
                if res.error:
                    return res

            return res.success(CoolNode(expr_node, pos_start, self.current_tok.pos_end.copy()))

        expr = res.register(self.expr())
        if res.error:
            return res
        return res.success(expr)

    def expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'forge'):
            res.register_advancement(); self.advance()

            if self.current_tok.type != TT_IDENT:
                return res.failure(ObsidianSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier after 'forge'"
                ))

            var_name = self.current_tok
            res.register_advancement(); self.advance()

            if self.current_tok.type != TT_EQ:
                return res.failure(ObsidianSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '=' after variable name"
                ))

            res.register_advancement(); self.advance()
            value_node = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarForgeNode(var_name, value_node))

        # Reassignment of an existing variable, e.g. `total = total + 1`
        # (distinct from `forge total = ...`, which declares a new one)
        if self.current_tok.type == TT_IDENT:
            start_idx = self.tok_idx
            var_name = self.current_tok
            res.register_advancement(); self.advance()

            if self.current_tok.type == TT_EQ:
                res.register_advancement(); self.advance()
                value_node = res.register(self.expr())
                if res.error:
                    return res
                return res.success(VarForgeNode(var_name, value_node))
            else:
                # Not an assignment after all — rewind and parse normally
                self.tok_idx = start_idx
                self.current_tok = self.tokens[self.tok_idx]

        node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))
        if res.error:
            return res
        return res.success(node)

    def comp_expr(self):
        res = ParseResult()
        node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))
        if res.error:
            return res
        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement(); self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        return self.bin_op(self.call, (TT_POW,), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
            return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement(); self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement(); self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(ObsidianSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ')', or an expression"
                    ))

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement(); self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(ObsidianSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ',' or ')'"
                    ))
                res.register_advancement(); self.advance()

            return res.success(CallNode(atom, arg_nodes))

        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement(); self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_STRING:
            res.register_advancement(); self.advance()
            return res.success(StringNode(tok))

        elif tok.type == TT_IDENT:
            res.register_advancement(); self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TT_LPAREN:
            res.register_advancement(); self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement(); self.advance()
                return res.success(expr)
            else:
                return res.failure(ObsidianSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"
                ))

        elif tok.matches(TT_KEYWORD, 'solid') or tok.matches(TT_KEYWORD, 'molten'):
            res.register_advancement(); self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.matches(TT_KEYWORD, 'crack'):
            crack_expr = res.register(self.crack_expr())
            if res.error:
                return res
            return res.success(crack_expr)

        elif tok.matches(TT_KEYWORD, 'erupt'):
            erupt_expr = res.register(self.erupt_expr())
            if res.error:
                return res
            return res.success(erupt_expr)

        elif tok.matches(TT_KEYWORD, 'mold'):
            mold_def = res.register(self.mold_def())
            if res.error:
                return res
            return res.success(mold_def)

        return res.failure(ObsidianSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, string, identifier, '+', '-', '(', 'crack', 'erupt' or 'mold'"
        ))

    def crack_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, 'crack'):
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'crack'"
            ))
        res.register_advancement(); self.advance()

        if self.current_tok.type != TT_LPAREN:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '('"
            ))
        res.register_advancement(); self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.type != TT_RPAREN:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"
            ))
        res.register_advancement(); self.advance()

        if self.current_tok.type != TT_LBRACE:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '{'"
            ))
        res.register_advancement(); self.advance()

        body = res.register(self.statements())
        if res.error:
            return res
        cases.append((condition, body))

        if self.current_tok.type != TT_RBRACE:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '}'"
            ))
        res.register_advancement(); self.advance()

        if self.current_tok.matches(TT_KEYWORD, 'shatter'):
            res.register_advancement(); self.advance()

            if self.current_tok.type != TT_LBRACE:
                return res.failure(ObsidianSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '{'"
                ))
            res.register_advancement(); self.advance()

            else_case = res.register(self.statements())
            if res.error:
                return res

            if self.current_tok.type != TT_RBRACE:
                return res.failure(ObsidianSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '}'"
                ))
            res.register_advancement(); self.advance()

        return res.success(CrackNode(cases, else_case))

    def erupt_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'erupt'):
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'erupt'"
            ))
        res.register_advancement(); self.advance()

        if self.current_tok.type != TT_LPAREN:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '('"
            ))
        res.register_advancement(); self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.type != TT_RPAREN:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"
            ))
        res.register_advancement(); self.advance()

        if self.current_tok.type != TT_LBRACE:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '{'"
            ))
        res.register_advancement(); self.advance()

        body = res.register(self.statements())
        if res.error:
            return res

        if self.current_tok.type != TT_RBRACE:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '}'"
            ))
        res.register_advancement(); self.advance()

        return res.success(EruptNode(condition, body))

    def mold_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'mold'):
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'mold'"
            ))
        res.register_advancement(); self.advance()

        var_name_tok = None
        if self.current_tok.type == TT_IDENT:
            var_name_tok = self.current_tok
            res.register_advancement(); self.advance()

        if self.current_tok.type != TT_LPAREN:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '(' or identifier"
            ))
        res.register_advancement(); self.advance()

        arg_name_toks = []
        if self.current_tok.type == TT_IDENT:
            arg_name_toks.append(self.current_tok)
            res.register_advancement(); self.advance()

            while self.current_tok.type == TT_COMMA:
                res.register_advancement(); self.advance()
                if self.current_tok.type != TT_IDENT:
                    return res.failure(ObsidianSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected identifier"
                    ))
                arg_name_toks.append(self.current_tok)
                res.register_advancement(); self.advance()

        if self.current_tok.type != TT_RPAREN:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected ',' or ')'"
            ))
        res.register_advancement(); self.advance()

        if self.current_tok.type != TT_LBRACE:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '{'"
            ))
        res.register_advancement(); self.advance()

        body = res.register(self.statements())
        if res.error:
            return res

        if self.current_tok.type != TT_RBRACE:
            return res.failure(ObsidianSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '}'"
            ))
        res.register_advancement(); self.advance()

        return res.success(MoldDefNode(var_name_tok, arg_name_toks, body))

    # ---------------------------
    # Helper for binary operations
    # ---------------------------

    def bin_op(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while (self.current_tok.type in ops) or ((self.current_tok.type, self.current_tok.value) in ops):
            op_tok = self.current_tok
            res.register_advancement(); self.advance()
            right = res.register(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)