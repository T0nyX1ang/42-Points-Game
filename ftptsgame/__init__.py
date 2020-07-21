"""Main module of this project."""

from .database import DATABASE_42
from .expr_utils import expr_eval, judge_equivalent
from .exceptions import FTPtsGameError
import random
import ast
import datetime


class FTPtsGame(object):
    """
    The main game.

    Available methods (+ means playing, - means not playing):
    __init__(): initialization. (Entry point)
    is_playing(): show the status of current game. (+-)
    generate_problem(): generate a problem from database or on custom. (-)
    get_elapsed_time(): get the time elapsed between solutions. (+)
    get_current_problem(): get current problem (tuple). (+)
    get_current_solutions(): get current solutions (list). (+)
    get_current_solution_number(): print current solution number. (+)
    get_total_solution_number(): print total solution number. (+)
    start(): start the game. (-)
    stop(): stop the game. (+)
    solve(): put forward a solution. (+)
    """

    def __init__(self):
        """Start the game session, serving as an initialization."""
        self.__valid = []  # this list stores readable answers
        self.__formula = []  # this list stores converted formulas
        self.__players = {}  # this dict stores player statistics
        self.__playing = False  # this stores playing status

    def __status_check(self, required_status: bool=True):
        """A status checker."""
        if required_status != self.is_playing():
            raise FTPtsGameError(0x00, required_status)

    def is_playing(self) -> bool:
        """Incicate the game is started or not."""
        return self.__playing

    def __refresh_timer(self):
        """Refresh the timer. Private method."""
        self.__timer = datetime.datetime.now()

    def get_elapsed_time(self) -> datetime.timedelta:
        """Get elapsed time between solutions. Effective when playing."""
        self.__status_check(required_status=True)
        elapsed = datetime.datetime.now() - self.__timer
        return elapsed

    def __generate_problem_from_database(self, **kwargs) -> tuple:
        """Generate a problem from database."""
        minimum_solutions = kwargs[
            'minimum_solutions'] if 'minimum_solutions' in kwargs else 3
        maximum_solutions = kwargs[
            'maximum_solutions'] if 'maximum_solutions' in kwargs else 100
        problem_list = [
            k for k in DATABASE_42.keys()
            if minimum_solutions <= DATABASE_42[k] <= maximum_solutions
        ]
        return random.choice(problem_list)

    def __generate_problem_by_user(self, **kwargs) -> tuple:
        """Generate a problem by user."""
        try:
            problem = tuple(sorted(list(kwargs['problem'])))
        except Exception as e:
            raise FTPtsGameError(0x01, e)
        if problem not in DATABASE_42:
            raise FTPtsGameError(0x02, problem)
        return problem

    def generate_problem(self, method: str, **kwargs) -> tuple:
        """Generate a random problem from the database."""
        self.__status_check(required_status=False)
        if method == 'database':
            self.__problem = self.__generate_problem_from_database(**kwargs)
        elif method == 'custom':
            self.__problem = self.__generate_problem_by_user(**kwargs)
        else:
            raise FTPtsGameError(0x02, method)

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
        return DATABASE_42[self.__problem]

    def get_current_player_statistics(self) -> dict:
        """Get current player statistics. Effective when playing."""
        self.__status_check(required_status=True)
        return self.__players

    def __validate_repeated(self, math_expr: str):
        """Validate distinguishing expressions. Private method."""
        for ind in range(0, len(self.__formula)):
            curr_expr = self.__formula[ind]
            if judge_equivalent(self.__problem, math_expr, curr_expr):
                raise FTPtsGameError(0x21, self.__valid[ind])

    def __update_player_statistics(self, player_id: int):
        """Update player statistics."""
        if player_id not in self.__players:
            self.__players[player_id] = [
                self.get_current_solution_number()
            ]
        else:
            self.__players[player_id].append(
                self.get_current_solution_number()
            )

    def solve(self, math_expr: str, player_id: int = -1) -> datetime.timedelta:
        """Put forward a solution."""
        self.__status_check(required_status=True)
        math_expr = math_expr.replace(' ', '').replace('（',
                                                       '(').replace('）', ')')

        if len(math_expr) >= 30:
            raise FTPtsGameError(0x10, len(math_expr))

        try:
            expr_ast = ast.parse(math_expr, mode='eval').body
        except Exception as e:
            raise FTPtsGameError(0x11, e)

        math_expr_value, simplified_expr, user_input_numbers = expr_eval(
            expr_ast, '', [])

        if math_expr_value != 42:
            raise FTPtsGameError(0x20, math_expr_value)

        if tuple(sorted(user_input_numbers)) != self.__problem:
            raise FTPtsGameError(0x15, tuple(sorted(user_input_numbers)))

        self.__validate_repeated(simplified_expr)
        self.__formula.append(simplified_expr)
        self.__valid.append(math_expr)
        self.__update_player_statistics(player_id)
        elapsed = self.get_elapsed_time()
        self.__refresh_timer()
        return elapsed

    def start(self):
        """Start the game. Effective when not playing."""
        self.__status_check(required_status=False)
        self.__valid = []
        self.__formula = []
        self.__players = {}
        self.__refresh_timer()
        self.__playing = True

    def stop(self):
        """Stop the game. Effective when playing."""
        self.__status_check(required_status=True)
        self.__playing = False
