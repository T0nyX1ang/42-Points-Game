"""42-points problem utilities for 42 points."""

from .expr_utils import Node
import random
from copy import deepcopy


class Problem(object):
    """A 42-points problem."""

    def __init__(self, problem):
        """Initialize the problem."""
        self.problem = sorted(problem)
        self.answer_table = []
        self.distinct_answer_table = []
        self.solution_number = -1
        self.equivalence_dict = {}
        self.parent = {}
        self.rank = {}

    def __all_expression_equals_to_target(self, target=42) -> list:
        """Get all possible answers of this problem."""
        return [
            deepcopy(expr) for expr in _get_all_expr(self.problem)
            if expr.evaluate() == target
        ]

    def __root(self, uid):
        """Method for union set."""
        if self.parent[uid] == uid:
            return uid
        else:
            self.parent[uid] = self.__root(self.parent[uid])
            return self.parent[uid]

    def __union(self, uid1, uid2):
        """Method for union set."""
        uid1 = self.__root(uid1)
        uid2 = self.__root(uid2)
        if uid1 != uid2:
            if self.rank[uid1] <= self.rank[uid2]:
                self.parent[uid1] = uid2
                self.rank[uid2] += (self.rank[uid1] == self.rank[uid2])
            else:
                self.parent[uid2] = uid1

    def __classify(self, target=42, max_number=13):
        """
        Divide all answers into some equivalence classes.

        Returns:
        1. A list including all answers (as expression trees);
        2. A dictionary, for any answer expression save the representative
           expression of its class (as the unique id of expressions).
        """
        values_list = []
        for _ in range(10):
            random_number = random.sample(range(500000, 1000000),
                                          max_number + 1)
            values = {i: random_number[i] for i in range(2, max_number + 1)}
            values[0], values[1] = 0, 1
            values_list.append(values)
        answers = self.__all_expression_equals_to_target(target)

        uid_table, uid_r1_table = {}, {}
        for expr in answers:
            uid = expr.unique_id()
            uid_table[uid] = expr
            uid_r1 = expr.unique_id_for_rule_1(values_list)
            if uid_r1 in uid_r1_table:
                self.parent[uid] = uid_r1_table[uid_r1]
                self.rank[uid] = 1
            else:
                self.parent[uid] = uid
                uid_r1_table[uid_r1] = uid
                self.rank[uid] = 2

        for expr in answers:
            uid1 = expr.unique_id()
            for expr2 in expr.all_equivalent_expression():
                uid2 = expr2.unique_id()
                self.__union(uid1, uid2)

        return_dict = {}
        for expr in answers:
            uid = expr.unique_id()
            return_dict[uid] = self.__root(uid)

        return answers, return_dict

    def generate_answers(self):
        """Generate all answers divided into equivalence classes."""
        self.answer_table, self.equivalence_dict = self.__classify()
        self.distinct_answer_table = []
        self.solution_number = 0
        for expr in self.answer_table:
            uid = expr.unique_id()
            if self.equivalence_dict[uid] == uid:
                self.distinct_answer_table.append(expr)
                self.solution_number += 1


def _get_all_expr(problem) -> list:
    """Return the list of all possible expressions of a problem."""
    n = len(problem)
    if n == 1:
        return [Node(Node.NODE_TYPE_NUMBER, problem[0])]
    return_list = []
    unique_id_set = set()
    for mask in range(1, 2 ** n - 1):
        t = mask
        left_prob = []
        right_prob = []
        for i in range(n):
            if t % 2 == 1:
                right_prob.append(problem[i])
            else:
                left_prob.append(problem[i])
            t //= 2
        left_set = _get_all_expr(left_prob)
        right_set = _get_all_expr(right_prob)
        for left_expr in left_set:
            for right_expr in right_set:
                for opt in '+-*/':
                    try:
                        expr = Node(Node.NODE_TYPE_OPERATOR, opt,
                                    left_expr, right_expr)
                        if expr.value < 0:
                            continue
                        expr_id = expr.unique_id()
                        if expr_id not in unique_id_set:
                            return_list.append(expr)
                            unique_id_set.add(expr_id)
                    except ArithmeticError:
                        pass
    return return_list
