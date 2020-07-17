"""Deal with expressions."""

from fractions import Fraction
from exceptions import UnsupportedSyntaxError
import ast
import random


def expr_eval(node, simplified, orig_num):
    """Evaluate a expression."""
    if isinstance(node, ast.BinOp):
        lval, left, orig_num = expr_eval(node.left, simplified, orig_num)
        op = node.op
        rval, right, orig_num = expr_eval(node.right, simplified, orig_num)

        # add parenthesis
        if isinstance(op, (ast.Mult, ast.Div)) and isinstance(
                node.left, ast.BinOp) and isinstance(node.left.op,
                                                     (ast.Add, ast.Sub)):
            left = '(%s)' % (left)

        if isinstance(op, (ast.Mult, ast.Div)) and isinstance(
                node.right, ast.BinOp) and isinstance(node.right.op,
                                                      (ast.Add, ast.Sub)):
            right = '(%s)' % (right)

        if isinstance(op, ast.Sub) and isinstance(
                node.right, ast.BinOp) and isinstance(node.right.op,
                                                      (ast.Add, ast.Sub)):
            right = '(%s)' % (right)

        if isinstance(op, ast.Div) and isinstance(
                node.right, ast.BinOp) and isinstance(node.right.op,
                                                      (ast.Mult, ast.Div)):
            right = '(%s)' % (right)

        # calculation and concatenation
        if isinstance(op, (ast.Add, ast.Sub)):
            if lval == 0:
                left = '0'
            if rval == 0:
                right = '0'

        if isinstance(op, (ast.Mult, ast.Div)):
            if lval == 1:
                left = '1'
            if rval == 1:
                right = '1'

        result, new_simplified = None, None
        if isinstance(op, ast.Add):
            result, new_simplified = lval + rval, left + '+' + right
        elif isinstance(op, ast.Sub):
            result, new_simplified = lval - rval, left + '-' + right
        elif isinstance(op, ast.Mult):
            result, new_simplified = lval * rval, left + '*' + right
        elif isinstance(op, ast.Div) and rval != 0:
            result, new_simplified = lval / rval, left + '/' + right
        elif isinstance(op, ast.Div) and rval == 0:
            raise UnsupportedSyntaxError('被除数为0')
        else:
            raise UnsupportedSyntaxError('不支持的运算符')
        return result, new_simplified, orig_num

    elif isinstance(node, ast.Num):
        number = node.n
        if type(number) is not int:
            raise UnsupportedSyntaxError('不支持浮点数计算')
        orig_num.append(number)
        if number not in [0, 1]:
            return Fraction(number), chr(number + 97), orig_num
        else:
            return Fraction(number), str(number), orig_num
    else:
        raise UnsupportedSyntaxError('不支持的运算符')


def judge_equivalent(problem, expr_1, expr_2):
    """Judge equivalent of two expressions."""
    count = 10
    random_number = random.sample(range(50000, 100000), len(problem) * count)
    for current in range(0, count):
        temp_expr_1, temp_expr_2 = expr_1, expr_2
        for i in range(0, len(problem)):
            temp_expr_1 = temp_expr_1.replace(
                chr(problem[i] + 97),
                str(random_number[i + current * len(problem)]))
            temp_expr_2 = temp_expr_2.replace(
                chr(problem[i] + 97),
                str(random_number[i + current * len(problem)]))
        temp_ast_1 = ast.parse(temp_expr_1, mode='eval').body
        temp_ast_2 = ast.parse(temp_expr_2, mode='eval').body
        if expr_eval(temp_ast_1, '',
                     [])[0] == expr_eval(temp_ast_2, '', [])[0]:
            return True
    return False
