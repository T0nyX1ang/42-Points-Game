"""Expression utilities for 42 points."""

import ast
from copy import deepcopy
from fractions import Fraction


class Node(object):
    """An expression tree."""

    NODE_TYPE_NUMBER = 0
    NODE_TYPE_OPERATOR = 1

    def __init__(self, type=NODE_TYPE_NUMBER, ch=None, left=None, right=None):
        """Initialize the node."""
        self.type = type
        self.left = left
        self.right = right
        if self.type == Node.NODE_TYPE_OPERATOR:
            self.value = Node.operation(ch, self.left.value, self.right.value)
            self.ch = ch
        else:
            self.value = Fraction(ch)
            self.ch = '#'

    @staticmethod
    def operation(opt, x, y):
        """Basic arithmetic operation between two numbers."""
        if opt == '/' and y == 0:
            raise ArithmeticError('Division by 0.')
        operation_list = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y
        }
        return operation_list[opt](x, y)

    def node_list(self) -> list:
        """Get the list of a node."""
        if self.type == Node.NODE_TYPE_OPERATOR:
            return self.left.node_list() + [self] + self.right.node_list()
        else:
            return [self]

    def unique_id(self) -> str:
        """Return the unique id (postfix) of this expression."""
        if self.type == Node.NODE_TYPE_OPERATOR:
            return self.ch + self.left.unique_id() + self.right.unique_id()
        else:
            return '[' + str(self.value) + ']'

    def __repr__(self) -> str:
        """Return the string form of this expression."""
        if self.type != Node.NODE_TYPE_OPERATOR:
            return str(self.value)

        deal_l = self.ch in '*/' and self.left.ch in '+-'
        deal_r = (self.ch in '-*/' and self.right.ch in '+-') or (
            self.ch == '/' and self.right.ch in '*/')
        left_string = '(' * deal_l + repr(self.left) + ')' * deal_l
        right_string = '(' * deal_r + repr(self.right) + ')' * deal_r
        return left_string + self.ch + right_string

    def evaluate(self, values: dict = None) -> Fraction:
        """Evaluate the value of this expression using substitution."""
        if values is None:
            return self.value
        if self.type == Node.NODE_TYPE_OPERATOR:
            return Node.operation(self.ch, self.left.evaluate(values),
                                  self.right.evaluate(values))
        else:
            return Fraction(values[int(self.value)])

    def extract(self) -> list:
        """Extract numbers from the node."""
        if self.type == Node.NODE_TYPE_OPERATOR:
            return self.left.extract() + self.right.extract()
        else:
            return [int(self.value)]

    def _reduce_subproc(self, left_value: Fraction,
                        right_value: Fraction,
                        return_value: Fraction):
        """Subprocedure for reduce_negative_number."""
        def neg(x, b):
            return x * (-1) ** b

        left_opt = 1
        right_opt = -1 if self.ch == '-' else 1

        left_value = neg(left_value, left_value < 0)
        left_opt = neg(left_opt, left_value < 0)
        right_value = neg(right_value, right_value < 0)
        right_opt = neg(right_opt, right_value < 0)
        left_opt = neg(left_opt, return_value < 0)
        right_opt = neg(right_opt, return_value < 0)

        if left_opt == 1:
            self.ch = '+' if right_opt == 1 else '-'
        else:
            self.ch = '-'
            self.left, self.right = self.right, self.left

    def reduce_negative_number(self):
        """
        Make all intermediate results of this expression not be negative.

        The result of whole expression will become its absolute value.
        """
        if self.type == Node.NODE_TYPE_OPERATOR:
            left_value = self.left.reduce_negative_number()
            right_value = self.right.reduce_negative_number()
            return_value = Node.operation(self.ch, left_value, right_value)
            if self.ch in '+-':
                self._reduce_subproc(left_value, right_value, return_value)
            self.value = abs(return_value)
            return return_value
        else:
            return self.value

    def all_equivalent_expression(self):
        """
        Return the list of all equivalent expression of an expression.

        Rule 1 (equivalence by identical equation) is not considered.
        If expression A induces expression B, B may not induce A.
        """
        if self.type != Node.NODE_TYPE_OPERATOR:
            return []

        return_list = []
        left_equal_list = self.left.all_equivalent_expression()
        right_equal_list = self.right.all_equivalent_expression()
        left_value, right_value = self.left.value, self.right.value
        for new_left in left_equal_list:
            return_list.append(
                Node(Node.NODE_TYPE_OPERATOR, self.ch, new_left,
                     deepcopy(self.right)))
        for new_right in right_equal_list:
            return_list.append(
                Node(Node.NODE_TYPE_OPERATOR, self.ch, deepcopy(self.left),
                     new_right))

        # Rule 2: x-0 --> x+0
        #         x/1 --> x*1
        #         0/x --> 0*x
        if self.ch == '-' and right_value == 0:
            return_list.append(
                Node(Node.NODE_TYPE_OPERATOR, '+', deepcopy(self.left),
                     deepcopy(self.right)))
        if self.ch == '/' and right_value == 1:
            return_list.append(
                Node(Node.NODE_TYPE_OPERATOR, '*', deepcopy(self.left),
                     deepcopy(self.right)))
        if self.ch == '/' and left_value == 0:
            return_list.append(
                Node(Node.NODE_TYPE_OPERATOR, '*', deepcopy(self.left),
                     deepcopy(self.right)))

        # Rule 3: (x?y)+0 --> (x+0)?y, x?(y+0)
        #         (x?y)*1 --> (x*1)?y, x?(y*1)
        if ((self.ch == '+' and right_value == 0) or
            (self.ch == '*' and right_value == 1)) \
                and self.left.type == Node.NODE_TYPE_OPERATOR:
            return_list.append(
                Node(
                    Node.NODE_TYPE_OPERATOR, self.left.ch,
                    Node(Node.NODE_TYPE_OPERATOR, self.ch,
                         deepcopy(self.left.left), deepcopy(self.right)),
                    deepcopy(self.left.right)))
            return_list.append(
                Node(
                    Node.NODE_TYPE_OPERATOR, self.left.ch,
                    deepcopy(self.left.left),
                    Node(Node.NODE_TYPE_OPERATOR, self.ch,
                         deepcopy(self.left.right), deepcopy(self.right))))

        # Rule 4: (y+z)/x --> (x-y)/z, (x-z)/y when x=y+z
        if self.ch == '/' and self.left.ch == '+' and \
                left_value == right_value and \
                self.left.left.value != 0 and self.left.right.value != 0:
            return_list.append(
                Node(
                    Node.NODE_TYPE_OPERATOR, '/',
                    Node(Node.NODE_TYPE_OPERATOR, '-',
                         deepcopy(self.right), deepcopy(self.left.left)),
                    deepcopy(self.left.right)))
            return_list.append(
                Node(
                    Node.NODE_TYPE_OPERATOR, '/',
                    Node(Node.NODE_TYPE_OPERATOR, '-',
                         deepcopy(self.right), deepcopy(self.left.right)),
                    deepcopy(self.left.left)))

        # Rule 5: x*(y/y) --> x+(y-y)
        if self.ch == '*' and self.right.ch == '/' and right_value == 1:
            return_list.append(
                Node(
                    Node.NODE_TYPE_OPERATOR, '+', deepcopy(self.left),
                    Node(Node.NODE_TYPE_OPERATOR, '-',
                         deepcopy(self.right.left),
                         deepcopy(self.right.right))))

        # Rule 6: x_1/x_2 --> x_2/x_1
        if self.ch == '/' and left_value == right_value:
            return_list.append(
                Node(Node.NODE_TYPE_OPERATOR, '/', deepcopy(self.right),
                     deepcopy(self.left)))

        # Rule 7: Changing two sub-expressions which have the same result
        #         doesn't change the equivalence class of this expression.
        left_node_list = self.left.node_list()
        right_node_list = self.right.node_list()
        for nl in left_node_list:
            for nr in right_node_list:
                if nl.value == nr.value:
                    nl.type, nl.left, nl.right, nl.ch, nl.value, \
                        nr.type, nr.left, nr.right, nr.ch, nr.value = \
                        nr.type, nr.left, nr.right, nr.ch, nr.value, \
                        nl.type, nl.left, nl.right, nl.ch, nl.value

                    return_list.append(deepcopy(self))

                    nl.type, nl.left, nl.right, nl.ch, nl.value, \
                        nr.type, nr.left, nr.right, nr.ch, nr.value = \
                        nr.type, nr.left, nr.right, nr.ch, nr.value, \
                        nl.type, nl.left, nl.right, nl.ch, nl.value

        # Rule 8: 2*2 --> 2+2
        #         4/2 --> 4-2
        if self.ch == '*' and left_value == 2 and right_value == 2:
            return_list.append(
                Node(Node.NODE_TYPE_OPERATOR, '+', deepcopy(self.left),
                     deepcopy(self.right)))
        if self.ch == '/' and left_value == 4 and right_value == 2:
            return_list.append(
                Node(Node.NODE_TYPE_OPERATOR, '-', deepcopy(self.left),
                     deepcopy(self.right)))

        return return_list

    def unique_id_for_rule_1(self, values_list):
        """
        Return the unique id of this expression.

        Two expressions is equivalent by rule 1 iff they have the same id.
        """
        results = [self.evaluate(values) for values in values_list]
        return tuple(results)


def _build_node(node):
    """Convert an AST node to an expression node."""
    node_ref = {
        type(ast.Add()): '+',
        type(ast.Sub()): '-',
        type(ast.Mult()): '*',
        type(ast.Div()): '/'
    }
    if isinstance(node, ast.BinOp) and type(node.op) in node_ref:
        built_node = Node(type=Node.NODE_TYPE_OPERATOR,
                          ch=node_ref[type(node.op)],
                          left=_build_node(node.left),
                          right=_build_node(node.right))
    elif isinstance(node, ast.Num) and type(node.n) is int and node.n in list(
            range(0, 14)):
        built_node = Node(type=Node.NODE_TYPE_NUMBER, ch=node.n)
    else:
        raise SyntaxError('Unallowed operator or operands.')
    return built_node


def build_node(token: str) -> Node:
    """Convert a token/string to an AST node."""
    token_ast = ast.parse(token, mode='eval').body
    node = _build_node(token_ast)
    node.reduce_negative_number()
    return node
