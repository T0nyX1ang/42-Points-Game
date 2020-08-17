import unittest
import datetime
import random
import time
from fractions import Fraction
from ftptsgame import FTPtsGame
from ftptsgame.database import DATABASE_42
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

        app.generate_problem('database')
        app.start()
        self.assertRaises(PermissionError, app.start)
        self.assertRaises(PermissionError, app.generate_problem, 'database', a=1, b=2)
        self.assertRaises(PermissionError, app.generate_problem, 'random', a=1, b=12345)
        self.assertRaises(PermissionError, app.generate_problem, 'custom', a='def', b='abc')

        app.stop()
        self.assertRaises(PermissionError, app.get_current_problem)
        self.assertRaises(PermissionError, app.get_current_solutions)
        self.assertRaises(PermissionError, app.get_current_solution_number)
        self.assertRaises(PermissionError, app.get_current_player_statistics)
        self.assertRaises(PermissionError, app.get_total_solution_number)
        self.assertRaises(PermissionError, app.get_elapsed_time)
        self.assertRaises(PermissionError, app.solve, '123' )
        self.assertRaises(PermissionError, app.stop)


    def test_game_problem_generator(self):
        # Game problem tests
        app = FTPtsGame()
        app.generate_problem('database', minimum_solutions=20, maximum_solutions=30)
        app.start()
        self.assertIn(app.get_current_problem(), DATABASE_42)
        self.assertIn(app.get_total_solution_number(), list(range(20, 31)))
        app.stop()

        app.generate_problem('database')
        app.start()
        self.assertIn(app.get_current_problem(), DATABASE_42)
        self.assertIn(app.get_total_solution_number(), list(range(1, 101)))
        app.stop()

        app.generate_problem('custom')
        app.start()
        self.assertIn(app.get_current_problem(), DATABASE_42)
        app.stop()

        self.assertRaises(ValueError, app.generate_problem, method='custom', problem='12345')
        self.assertRaises(TypeError, app.generate_problem, method='custom', problem=123)
        self.assertRaises(ValueError, app.generate_problem, method='custom', problem=[0, 0, 0, 0, 0])
        
        app.generate_problem('custom', problem=[6, 0, 0, 7, 0])
        app.start()
        self.assertEqual((0, 0, 0, 6, 7), app.get_current_problem())
        app.stop()

        app.generate_problem(method='probability')
        app.start()
        self.assertIn(app.get_current_problem(), DATABASE_42)
        app.stop()
        self.assertRaises(TypeError, app.generate_problem, method='probability', prob=123)
        self.assertRaises(ValueError, app.generate_problem, method='probability', prob=[1, 2, 2])
        test_prob = [0] * len(DATABASE_42.keys())
        r = random.randint(0, len(DATABASE_42.keys()) - 1)
        test_prob[r] = 100
        app.generate_problem('probability', prob=test_prob)
        app.start()
        self.assertEqual(list(DATABASE_42.keys())[r], app.get_current_problem()) 
        app.stop()

        self.assertRaises(TypeError, app.generate_problem, method='wrong_method', problem=[6, 7, 0, 0, 0])


    def test_game_process(self):
        # Game process tests
        app = FTPtsGame()
        app.generate_problem('custom', problem=[3, 4, 6, 7, 12])
        app.start()
        self.assertIs(type(app.get_elapsed_time()), datetime.timedelta)
        self.assertEqual(app.get_total_solution_number(), DATABASE_42[(3, 4, 6, 7, 12)])
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

        s2 = app.solve('       （12      +      6  /     3)  *  （7    -   4)')
        self.assertIs(type(s2), datetime.timedelta)
        self.assertEqual(app.get_current_player_statistics(), [(10000, s1), (-1, s2)])
        self.assertEqual(['6*7+(12-3*4)', '(12+6/3)*(7-4)'], app.get_current_solutions())
        app.stop()
    
    def test_throttle(self):
        # throttle tests for game time
        app = FTPtsGame()
        app.generate_problem('custom', problem=(1, 1, 6, 7, 12))
        app.start()
        answer = ['((1+12)-(1+6))*7', '6*(((12-7)+1)+1)', '((12*(1-1))+6)*7', '12/(1+((1-6)/7))', '12+((1-6)*(1-7))', '((1+12)-6)*(7-1)', '((1+12)-7)*(6+1)', '12-(((1+1)-7)*6)', '(6*((7+1)+1))-12']
        for ans in answer:
            time.sleep(1)
            s_time = app.solve(ans)
            self.assertLess(abs(s_time.seconds - 1), 2)
        f_time = app.stop()
        self.assertLess(abs(f_time.seconds - len(answer)), 2)

    def test_standalone_expr_utils(self):
        # additional tests for other issued problems
        n1 = build_node('2-4*10*(7-8)')
        n2 = build_node('10*4*(8-7)+2')
        self.assertFalse(n1 != n2)
