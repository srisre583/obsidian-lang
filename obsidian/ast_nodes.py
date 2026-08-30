# ast_nodes.py

class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class VarAccessNode:
    """Reading a variable's value, e.g. `x`"""
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.pos_start = var_name_tok.pos_start
        self.pos_end = var_name_tok.pos_end


class VarForgeNode:
    """Declaring/assigning a variable, e.g. `forge x = 5`"""
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = var_name_tok.pos_start
        self.pos_end = value_node.pos_end


class BinOpNode:
    """A binary operation, e.g. `5 + 3`"""
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = left_node.pos_start
        self.pos_end = right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    """A unary operation, e.g. `-5`"""
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class CrackNode:
    """An if/else chain: `crack (...) { ... } shatter { ... }`"""
    def __init__(self, cases, else_case):
        # cases: list of (condition_node, body_node) tuples
        # else_case: body_node or None
        self.cases = cases
        self.else_case = else_case
        self.pos_start = cases[0][0].pos_start
        self.pos_end = (else_case or cases[-1][1]).pos_end


class EruptNode:
    """A while loop: `erupt (...) { ... }`"""
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node
        self.pos_start = condition_node.pos_start
        self.pos_end = body_node.pos_end


class MoldDefNode:
    """A function definition: `mold name(args) { ... }`"""
    def __init__(self, var_name_tok, arg_name_toks, body_node):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node

        if var_name_tok:
            self.pos_start = var_name_tok.pos_start
        elif len(arg_name_toks) > 0:
            self.pos_start = arg_name_toks[0].pos_start
        else:
            self.pos_start = body_node.pos_start

        self.pos_end = body_node.pos_end


class CallNode:
    """Calling a function: `name(args)`"""
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = node_to_call.pos_start
        if len(arg_nodes) > 0:
            self.pos_end = arg_nodes[-1].pos_end
        else:
            self.pos_end = node_to_call.pos_end


class CoolNode:
    """A return statement: `cool value`"""
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return
        self.pos_start = pos_start
        self.pos_end = pos_end


class ListNode:
    """A sequence of statements/expressions"""
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end