"""Main module of this project."""

from .expr_utils import Node, build_node
from .problem_utils import Problem
import datetime


class FTPtsGame(object):
    """
    The main game.

    Available methods (+ means playing, - means not playing):
    __init__(): initialization. (Entry point)
    is_playing(): show the status of current game. (+-)
    generate_problem(): generate a problem manually. (-)
    get_elapsed_time(): get the time elapsed during the game. (+)
    get_current_problem(): get current problem (tuple). (+)
    get_current_solutions(): get current solutions (list). (+)
    get_current_solution_number(): print current solution number. (+)
    get_total_solution_number(): print total solution number. (+)
    start(): start the game. (-)
    stop(): stop the game. (+)
    solve(): put forward a solution and show solution intervals. (+)
    """

    def __init__(self):
        """Start the game session, serving as an initialization."""
        self.__valid = []  # this list stores readable answers
        self.__formula = []  # this list stores converted formulas
        self.__players = []  # this list stores player statistics
        self.__playing = False  # this stores playing status

    def __status_check(self, required_status: bool = True):
        """A status checker."""
        if required_status != self.is_playing():
            raise PermissionError('Required status: %s' % required_status)

    def is_playing(self) -> bool:
        """Indicate the game is started or not."""
        return self.__playing

    def get_elapsed_time(self) -> datetime.timedelta:
        """Get elapsed time between solutions. Effective when playing."""
        self.__status_check(required_status=True)
        elapsed = datetime.datetime.now() - self.__timer
        return elapsed

    def generate_problem(self, problem):
        """Generate a problem manually."""
        self.__status_check(required_status=False)
        self.__problem = tuple(sorted(problem))
        self.__problem_class = Problem(list(self.__problem))
        self.__problem_class.generate_answers()
        if len(self.__problem_class.distinct_answer_table) == 0:
            raise ValueError('No solution found.')

    def get_current_problem(self) -> tuple:
        """Get current problem. Effective when playing."""
        self.__status_check(required_status=True)
        return self.__problem

    def get_current_solutions(self) -> list:
        """Get current valid solutions. Effective when playing."""
        self.__status_check(required_status=True)
        return self.__valid

    def get_current_solution_number(self) -> int:
        """Get the number of current solutions. Effective when playing."""
        self.__status_check(required_status=True)
        return len(self.__valid)

    def get_total_solution_number(self) -> int:
        """Get the number of total solutions. Effective when playing."""
        self.__status_check(required_status=True)
        return len(self.__problem_class.distinct_answer_table)

    def get_remaining_solutions(self) -> list:
        """Get remaining solutions. Effective when playing."""
        self.__status_check(required_status=True)
        current_solution_set = set()
        for expr_str in self.__valid:
            node = build_node(expr_str)
            current_solution_set.add(
                self.__problem_class.equivalence_dict[node.unique_id()])
        return_list = []
        for expr in self.__problem_class.distinct_answer_table:
            if self.__problem_class.equivalence_dict[
                    expr.unique_id()] not in current_solution_set:
                return_list.append(str(expr))
        return return_list

    def get_current_player_statistics(self) -> list:
        """Get current player statistics. Effective when playing."""
        self.__status_check(required_status=True)
        return self.__players

    def __validate_repeated(self, node: Node):
        """Validate distinguishing expressions. Private method."""
        class_id = self.__problem_class.equivalence_dict[node.unique_id()]
        for ind in range(0, len(self.__formula)):
            cmp_node = self.__formula[ind]
            cmp_class_id = self.__problem_class.equivalence_dict[
                cmp_node.unique_id()]
            if cmp_class_id == class_id:
                raise LookupError(self.__valid[ind])

    def solve(self, math_expr: str, player_id: int = -1) -> datetime.timedelta:
        """Put forward a solution and show solution intervals if correct."""
        self.__status_check(required_status=True)

        replace_table = [
            ('×', '*'), ('x', '*'), ('÷', '/'), (' ', ''),
            ('\n', ''), ('\r', ''), ('（', '('), ('）', ')'),
        ]
        for src, dest in replace_table:
            math_expr = math_expr.replace(src, dest)

        if len(math_expr) >= 30:
            raise OverflowError('Maximum parsing length exceeded.')

        node = build_node(math_expr)
        math_expr_value = node.evaluate()
        user_input_numbers = node.extract()
        if math_expr_value != 42:
            raise ArithmeticError(str(math_expr_value))
        if tuple(sorted(user_input_numbers)) != self.__problem:
            raise ValueError('Unmatched input numbers.')

        self.__validate_repeated(node)
        self.__formula.append(node)
        self.__valid.append(math_expr)
        elapsed = self.get_elapsed_time()
        interval = elapsed - self.__last
        self.__last = elapsed
        self.__players.append((player_id, interval))
        return interval

    def start(self):
        """Start the game. Effective when not playing."""
        self.__status_check(required_status=False)
        self.__valid = []
        self.__formula = []
        self.__players = []
        self.__timer = datetime.datetime.now()
        self.__last = datetime.timedelta(seconds=0)  # A tag for each solution.
        self.__playing = True

    def stop(self) -> datetime.timedelta:
        """Stop the game. Effective when playing."""
        self.__status_check(required_status=True)
        elapsed = self.get_elapsed_time()
        self.__playing = False
        return elapsed
