"""42-points problem utilities for 42 points."""

from .expr_utils import Node
import itertools
import random
from copy import deepcopy

import time


class Problem(object):
    """A 42-points problem."""

    def __init__(self, problem):
        """Initialize the problem."""
        self.problem = problem
        self.answer_table = []
        self.distinct_answer_table = []
        self.solution_number = -1
        self.equivalence_dict = {}
        self.problem.sort()

    @staticmethod
    def __all_expression_recursive(prob) -> list:
        """Return the list of all possible expressions of a problem."""
        n = len(prob)
        if n == 0:
            return []
        if n == 1:
            return [Node(Node.NODE_TYPE_NUMBER, prob[0])]
        return_list = []
        unique_id_set = set()
        for mask in range(1, 2 ** n - 1):
            left_prob = []
            right_prob = []
            t = mask
            for i in range(n):
                if t % 2 == 1:
                    right_prob.append(prob[i])
                else:
                    left_prob.append(prob[i])
                t //= 2
            left_set = Problem.__all_expression_recursive(left_prob)
            right_set = Problem.__all_expression_recursive(right_prob)
            for left_expr in left_set:
                for right_expr in right_set:
                    for opt in '+-*/':
                        try:
                            expr = Node(Node.NODE_TYPE_OPERATOR, opt, left_expr, right_expr)
                            if expr.value < 0:
                                continue
                            expr_id = expr.unique_id()
                            if expr_id not in unique_id_set:
                                return_list.append(expr)
                                unique_id_set.add(expr_id)
                        except ArithmeticError:
                            pass
        return return_list

    def __all_expression(self) -> list:
        """Return the list of all possible expressions of this problem."""
        return Problem.__all_expression_recursive(self.problem)

    def __all_expression_equals_to_target(self, target=42) -> list:
        """Return the list of all possible answers of this problem (must be equal to the target)."""
        return [deepcopy(expr) for expr in self.__all_expression() if expr.evaluate() == target]

    def __all_answer_divided_into_equivalence_classes(self, rule_set="Tony", target=42, max_number=13):
        """Divide all answer into some equivalence classes.
           Return two objects:
           1. A list including all answers (as expression trees);
           2. A dictionary, for any answer expression save the representative expression of its class
              (as the unique id of expressions)."""
        if rule_set in ['Tony', 'Misaka']:
            values_list = []
            for _ in range(10):
                random_number = random.sample(range(500000, 1000000), max_number + 1)
                values = {i: random_number[i] for i in range(2, max_number + 1)}
                values[0] = 0
                values[1] = 1
                values_list.append(values)
            answers = self.__all_expression_equals_to_target(target)
            parent, rank = {}, {}
            uid_table, uid_r1_table = {}, {}
            for expr in answers:
                uid = expr.unique_id()
                uid_table[uid] = expr
                uid_r1 = expr.unique_id_for_rule_1(values_list)
                if uid_r1 in uid_r1_table:
                    parent[uid] = uid_r1_table[uid_r1]
                    rank[uid] = 1
                else:
                    parent[uid] = uid
                    uid_r1_table[uid_r1] = uid
                    rank[uid] = 2

            def root(uid):
                nonlocal parent
                if parent[uid] == uid:
                    return uid
                else:
                    parent[uid] = root(parent[uid])
                    return parent[uid]

            def union(uid1, uid2):
                nonlocal parent, rank
                uid1, uid2 = root(uid1), root(uid2)
                if uid1 != uid2:
                    if rank[uid1] <= rank[uid2]:
                        parent[uid1] = uid2
                        if rank[uid1] == rank[uid2]:
                            rank[uid2] += 1
                    else:
                        parent[uid2] = uid1

            for expr in answers:
                uid1 = expr.unique_id()
                for expr2 in expr.all_equivalent_expression(rule_set):
                    uid2 = expr2.unique_id()
                    union(uid1, uid2)
            return_dict = {}
            for expr in answers:
                uid = expr.unique_id()
                return_dict[uid] = root(uid)
            return answers, return_dict
        return [], {}

    def generate_answers(self, rule_set="Tony"):
        """Generate all answers divided into equivalence classes."""
        self.answer_table, self.equivalence_dict = self.__all_answer_divided_into_equivalence_classes(rule_set)
        self.distinct_answer_table = []
        self.solution_number = 0
        for expr in self.answer_table:
            uid = expr.unique_id()
            if self.equivalence_dict[uid] == uid:
                self.distinct_answer_table.append(expr)
                self.solution_number += 1


def generate_database(rule_set="Tony"):
    """Update database.py."""
    problem_size = 5
    max_number = 13
    number_pool = list(range(max_number + problem_size))
    f = open('database-%s.py' % rule_set, 'w')
    f.write('''"""
Global database for this project.

This database can be re-generated by command line.
"""


DATABASE_42 = {
''')
    f2 = open('42-detail-%s.txt' % rule_set, 'w')
    first_flag = True
    for problem_tuple in itertools.combinations(number_pool, problem_size):
        problem = list(problem_tuple)
        for i in range(problem_size):
            problem[i] -= i
        print(problem, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        problem_class = Problem(problem)
        problem_class.generate_answers(rule_set)
        m = len(problem_class.distinct_answer_table)
        if m == 0:
            continue
        if first_flag:
            f.write('    %s: %d' % (str(tuple(problem)), m))
        else:
            f.write(',\n    %s: %d' % (str(tuple(problem)), m))
        print(' '.join([str(x) for x in problem]) + '  solution_number=%d' % m, file=f2)
        for expr in problem_class.distinct_answer_table:
            print(expr.to_string(), file=f2)
        print(file=f2)
        print(problem)
        first_flag = False
    f.write('''
}
''')
    f.close()
