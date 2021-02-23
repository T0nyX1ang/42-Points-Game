import unittest
import datetime
import random
import time
from fractions import Fraction
from ftptsgame import FTPtsGame
from ftptsgame.expr_utils import build_node

class TestGameApp(unittest.TestCase):
    def test_game_status(self):
        app = FTPtsGame()
        self.assertRaises(PermissionError, app.get_current_problem)
        self.assertRaises(PermissionError, app.get_current_solutions)
        self.assertRaises(PermissionError, app.get_current_solution_number)
        self.assertRaises(PermissionError, app.get_current_player_statistics)
        self.assertRaises(PermissionError, app.get_total_solution_number)
        self.assertRaises(PermissionError, app.get_elapsed_time)
        self.assertRaises(PermissionError, app.solve, '123')
        self.assertRaises(PermissionError, app.stop)

        app.generate_problem(problem=[0, 0, 0, 6, 7])
        app.start()
        self.assertRaises(PermissionError, app.start)
        self.assertRaises(PermissionError, app.generate_problem, problem=[0, 0, 0, 6, 7])

        app.stop()
        self.assertRaises(PermissionError, app.get_current_problem)
        self.assertRaises(PermissionError, app.get_current_solutions)
        self.assertRaises(PermissionError, app.get_current_solution_number)
        self.assertRaises(PermissionError, app.get_current_player_statistics)
        self.assertRaises(PermissionError, app.get_total_solution_number)
        self.assertRaises(PermissionError, app.get_elapsed_time)
        self.assertRaises(PermissionError, app.get_remaining_solutions)
        self.assertRaises(PermissionError, app.solve, '123' )
        self.assertRaises(PermissionError, app.stop)

    def test_game_problem_generator(self):
        # Game problem tests
        app = FTPtsGame()        
        app.generate_problem(problem=[6, 0, 0, 7, 0])
        app.start()
        self.assertEqual((0, 0, 0, 6, 7), app.get_current_problem())
        self.assertEqual(1, app.get_total_solution_number())
        app.stop()

    def test_game_process(self):
        # Game process tests
        app = FTPtsGame()
        self.assertRaises(ValueError, app.generate_problem, [0, 0, 0, 5, 6])
        self.assertRaises(ValueError, app.generate_problem, [0, 0, 0, 5, 7])
        self.assertRaises(ValueError, app.generate_problem, [0, 0, 1, 5, 5])
        self.assertRaises(ValueError, app.generate_problem, [13, 13, 13, 13, 13])

        app.generate_problem(problem=[3, 4, 6, 7, 12])
        app.start()
        self.assertIs(type(app.get_elapsed_time()), datetime.timedelta)
        self.assertEqual(app.get_total_solution_number(), 26)
        self.assertRaises(SyntaxError, app.solve, '')
        self.assertRaises(OverflowError, app.solve, '1'*30)
        self.assertRaises(ArithmeticError, app.solve, '1')
        self.assertRaises(SyntaxError, app.solve, '1+')
        self.assertRaises(SyntaxError, app.solve, '1+(')
        self.assertRaises(SyntaxError, app.solve, '42')
        self.assertRaises(ValueError, app.solve, '1+2+3+4+5+6+7+8+9-3')
        self.assertRaises(SyntaxError, app.solve, '-1+3')
        self.assertRaises(ArithmeticError, app.solve, '1-(3-1)')
        self.assertRaises(SyntaxError, app.solve, '1**3')
        self.assertRaises(SyntaxError, app.solve,'1+3.0')
        self.assertRaises(ArithmeticError, app.solve,'1/0')
        self.assertEqual([], app.get_current_solutions())

        s1 = app.solve('6*7+(12-3*4)', player_id=10000)
        self.assertIs(type(s1), datetime.timedelta)
        self.assertEqual(app.get_current_player_statistics(), [(10000, s1)])
        self.assertRaises(SyntaxError, app.solve, '___123456___')
        self.assertRaises(SyntaxError, app.solve, '111111+ 22222 +33333 +55555')
        # self.assertRaises(FTPtsGameError, app.solve, '6*(7 / 12)*3*4')
        self.assertRaises(LookupError, app.solve, '12/(3*4)*6*7')
        self.assertRaises(LookupError, app.solve, '6*7*(12 / (3*4))')
        self.assertRaises(LookupError, app.solve, '(12-3*4)+6*7')
        self.assertEqual(app.get_current_solution_number(), 1)
        self.assertEqual(len(app.get_remaining_solutions()), 25)

        s2 = app.solve('       （12      +      6  /     3)  *  （7    -   4)')
        self.assertRaises(LookupError, app.solve, '(4-7)*(12+6/3)')
        self.assertIs(type(s2), datetime.timedelta)
        self.assertEqual(app.get_current_player_statistics(), [(10000, s1), (-1, s2)])
        self.assertEqual(['6*7+(12-3*4)', '(12+6/3)*(7-4)'], app.get_current_solutions())
        app.stop()

    
    def test_throttle(self):
        # throttle tests for game time
        app = FTPtsGame()
        app.generate_problem(problem=[1, 1, 6, 7, 12])
        app.start()
        answer = ['(12*(1-1)+7)*6', '(12-7+1)*(6+1)', '12+(7-1)*(6-1)', '12/(1-(6-1)/7)', '(7+1+1)*6-12']
        for ans in answer:
            time.sleep(1)
            s_time = app.solve(ans)
            self.assertLess(abs(s_time.seconds - 1), 2)
        f_time = app.stop()
        self.assertLess(abs(f_time.seconds - len(answer)), 2)

    def test_standalone_expr_utils(self):
        # additional tests for other issued problems
        a = build_node('(1-2)*(3-4-5)')
        self.assertEqual(str(a), '(2-1)*(4-3+5)')
        a = build_node('(1-2)*(3-4+5)')
        self.assertEqual(str(a), '(2-1)*(5-(4-3))')
        a = build_node('(1-2)*(4+5-3)')
        self.assertEqual(str(a), '(2-1)*(4+5-3)')
        a = build_node('(2-1)*(3-4-5)')
        self.assertEqual(str(a), '(2-1)*(4-3+5)')
        a = build_node('(3-4-5)*(2-1)')
        self.assertEqual(str(a), '(4-3+5)*(2-1)')
        a = build_node('9/(11/6-2)+12')
        self.assertEqual(str(a), '9/(2-11/6)-12')

    def test_different_targets(self):
        # additional tests for different target
        app = FTPtsGame(target=48)
        app.generate_problem(problem=[3, 4, 6, 8, 12])
        app.start()
        self.assertEqual(app.get_total_solution_number(), 48)
        app.solve('4/3*(6*8-12)')
        self.assertRaises(ArithmeticError, app.solve, '12*(8-4-3/6)')
        self.assertRaises(LookupError, app.solve, '4*(6*8-12)/3')
        app.stop()
