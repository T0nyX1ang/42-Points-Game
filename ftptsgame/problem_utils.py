"""42-points problem utilities for 42 points."""

import random
import itertools
from .expr_utils import Node


class Problem(object):
    """A 42-points problem."""

    def __init__(self, problem):
        """Initialize the problem."""
        self.problem = sorted(problem)
        self.answer_table = []
        self.distinct_answer_table = []
        self.equivalence_dict = {}
        self.__parent = {}
        self.__rank = {}

    def __root(self, uid):
        """Method for union set."""
        if self.__parent[uid] == uid:
            return uid
        else:
            self.__parent[uid] = self.__root(self.__parent[uid])
            return self.__parent[uid]

    def __union(self, uid1, uid2):
        """Method for union set."""
        uid1 = self.__root(uid1)
        uid2 = self.__root(uid2)
        if uid1 != uid2:
            if self.__rank[uid1] <= self.__rank[uid2]:
                self.__parent[uid1] = uid2
                self.__rank[uid2] += (self.__rank[uid1] == self.__rank[uid2])
            else:
                self.__parent[uid2] = uid1

    def __classify(self, target):
        """
        Divide all answers into some equivalence classes.

        Returns:
        1. A list including all answers (as expression trees);
        2. A dictionary, for any answer expression save the representative
           expression of its class (as the unique id of expressions).
        """
        values_list = []
        n = len(self.problem)
        dif = list(set(self.problem))  # different numbers of the problem
        for _ in range(10):
            numbers = random.sample(range(500000, 1000000), len(dif))
            values = {dif[i]: numbers[i] for i in range(len(dif))}
            values[0], values[1] = 0, 1
            values_list.append(values)
        answers = _get_all_expr(self.problem, n, target)

        uid_table, uid_r1_table = {}, {}
        for expr in answers:
            uid = expr.unique_id()
            uid_table[uid] = expr
            uid_r1 = expr.unique_id_for_rule_1(values_list)
            if uid_r1 in uid_r1_table:
                self.__parent[uid] = uid_r1_table[uid_r1]
                self.__rank[uid] = 1
            else:
                self.__parent[uid] = uid
                uid_r1_table[uid_r1] = uid
                self.__rank[uid] = 2

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

    def generate_answers(self, target: int = 42):
        """Generate all answers divided into equivalence classes."""
        self.answer_table, self.equivalence_dict = self.__classify(target)
        self.distinct_answer_table = []
        for expr in self.answer_table:
            uid = expr.unique_id()
            if self.equivalence_dict[uid] == uid:
                self.distinct_answer_table.append(expr)


def _combine_expr(left_set: list, right_set: list):
    """Combine two node sets to a single node set with different operators."""
    for left_expr, right_expr in itertools.product(left_set, right_set):
        yield Node(Node.NODE_TYPE_OPERATOR, '+', left_expr, right_expr)

        yield Node(Node.NODE_TYPE_OPERATOR, '*', left_expr, right_expr)

        if left_expr.value >= right_expr.value:
            yield Node(Node.NODE_TYPE_OPERATOR, '-', left_expr, right_expr)

        if right_expr.value != 0:
            yield Node(Node.NODE_TYPE_OPERATOR, '/', left_expr, right_expr)


def _get_all_expr(problem: list, length: int, target: int) -> list:
    """Return the list of all possible expressions of a problem."""
    n = len(problem)
    if n == 1:
        return [Node(Node.NODE_TYPE_NUMBER, problem[0])]
    return_list = []
    unique_id_set = set()

    for mask in itertools.filterfalse(
        lambda x: sum(x) == 0 or sum(x) == n,
        itertools.product([0, 1], repeat=n)
    ):
        left_prob, right_prob = [], []
        for i in range(n):
            left_prob.append(problem[i]) if mask[i] == 0 \
                else right_prob.append(problem[i])

        left_set = _get_all_expr(left_prob, length, target)
        right_set = _get_all_expr(right_prob, length, target)

        for expr in itertools.filterfalse(
            lambda x: x.value != target and n == length,
            _combine_expr(left_set, right_set)
        ):
            expr_id = expr.unique_id()
            if expr_id not in unique_id_set:
                return_list.append(expr)
                unique_id_set.add(expr_id)

    return return_list
