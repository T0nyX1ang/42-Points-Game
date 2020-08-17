"""Expression utilities for 42 points."""

import ast
import math
import random
from fractions import Fraction


class Node(object):
    """Simple implementation of an expression tree."""

    def __init__(self, ch=None, left=None, right=None):
        """Initialize the node."""
        self.ch = ch
        self.left = left
        self.right = right

    def __eq__(self, node):
        """Judge equivalence two expressions."""
        for _ in range(0, 10):
            v_test = self.__generate_values(random_value=True)
            if self.evaluate(v_test) == node.evaluate(v_test):
                return True
        return False

    def __ne__(self, node):
        """Judge in-equivalence two expressions."""
        return not self.__eq__(node)

    def __pre_simplify_validation(self, value, parent_ch):
        """Validation before simplication of the formula."""
        add_sub_check = (value == 0 and parent_ch in '+-')
        mult_div_check = (abs(value) == 1 and parent_ch in '*/')
        return add_sub_check or mult_div_check

    def __generate_values(self, random_value=False):
        """Generate normal or random values."""
        if random_value:
            random_number = random.sample(range(500000, 1000000), 14)
            result = {chr(i + 97): random_number[i] for i in range(0, 14)}
        else:
            result = {chr(i + 97): i for i in range(0, 14)}
        result['0'], result['1'], result['-1'] = 0, 1, -1  # forcibly replace
        return result

    def evaluate(self, values: dict = {}) -> Fraction:
        """Evaluate the value of the node using a substitute dictionary."""
        if not values:
            values = self.__generate_values()

        operation = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y if y != 0 else math.inf
        }

        if self.ch in '+-*/':
            return operation[self.ch](self.left.evaluate(values),
                                      self.right.evaluate(values))
        else:
            return Fraction(values[self.ch])

    def extract(self) -> list:
        """Extract numbers from the node."""
        numbers = []
        v_normal = self.__generate_values()
        if self.ch not in '+-*/':
            numbers.append(v_normal[self.ch])
        else:
            numbers = self.left.extract() + self.right.extract()
        return numbers

    def simplify(self):
        """Simplify the node."""
        if self.ch in '+-*/':
            l_value = self.left.evaluate()
            r_value = self.right.evaluate()
            new_node_left = Node(
                ch=str(l_value)) if self.__pre_simplify_validation(
                    l_value, self.ch) else self.left.simplify()
            new_node_right = Node(
                ch=str(r_value)) if self.__pre_simplify_validation(
                    r_value, self.ch) else self.right.simplify()
            new_node = Node(ch=self.ch,
                            left=new_node_left,
                            right=new_node_right)
        else:
            new_node = Node(ch=self.ch) if self.ch not in 'ab' else Node(
                ch=str(ord(self.ch) - 97))

        return new_node


def _build_node(node):
    """Convert an AST node to an expression node."""
    node_ref = {
        type(ast.Add()): '+',
        type(ast.Sub()): '-',
        type(ast.Mult()): '*',
        type(ast.Div()): '/'
    }
    if isinstance(node, ast.BinOp) and type(node.op) in node_ref:
        built_node = Node(ch=node_ref[type(node.op)],
                          left=_build_node(node.left),
                          right=_build_node(node.right))
    elif isinstance(node, ast.Num) and type(node.n) is int and node.n in list(
            range(0, 14)):
        built_node = Node(ch=chr(97 + node.n))
    else:
        raise SyntaxError('Unallowed operator or operands.')
    return built_node


def build_node(token: str) -> Node:
    """Convert a token/string to an AST node."""
    token_ast = ast.parse(token, mode='eval').body
    return _build_node(token_ast)
