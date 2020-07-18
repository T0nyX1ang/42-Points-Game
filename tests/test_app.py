import unittest
from ftptsgame import GameApp
from ftptsgame.exceptions import *
from ftptsgame.database import DATABASE_42

class TestGameApp(unittest.TestCase):
    def test_game_app(self):
        app = GameApp()
        # Status checker tests
        self.assertRaises(GameStatusError, app.get_current_problem)
        self.assertRaises(GameStatusError, app.get_current_solved)
        self.assertRaises(GameStatusError, app.get_current_solution_number)
        self.assertRaises(GameStatusError, app.get_total_solution_number)
        self.assertRaises(GameStatusError, app.solve, '123')
        self.assertRaises(GameStatusError, app.stop)

        # Game tests
        app.generate_problem(60, 61)
        app.start()
        self.assertRaises(GameStatusError, app.start)
        self.assertRaises(GameStatusError, app.generate_problem, 1, 2)
        self.assertEqual(app.get_total_solution_number(), DATABASE_42[(3, 4, 6, 7, 12)])
        # self.assertRaises(UnsupportedSyntaxError, app.solve, '')
        self.assertRaises(UnsupportedSyntaxError, app.solve, '1'*30)
        self.assertRaises(WrongAnswerError, app.solve, '1')
        # self.assertRaises(UnsupportedSyntaxError, app.solve, '1+')
        # self.assertRaises(UnsupportedSyntaxError, app.solve, '1+(')
        self.assertRaises(UnmatchedNumberError, app.solve, '42')
        self.assertRaises(UnsupportedSyntaxError, app.solve, '-1+3')
        self.assertRaises(WrongAnswerError, app.solve, '1-(3-1)')
        self.assertRaises(UnsupportedSyntaxError, app.solve, '1**3')
        self.assertRaises(UnsupportedSyntaxError, app.solve,'-1+3')
        self.assertRaises(UnsupportedSyntaxError, app.solve,'1+3.0')
        self.assertRaises(UnsupportedSyntaxError, app.solve,'1/0')
        self.assertEqual('当前暂无有效求解', app.get_current_solved())
        app.solve('6*7+(12-3*4)')
        self.assertRaises(UnsupportedSyntaxError, app.solve, '___123456___')
        # self.assertRaises(UnsupportedSyntaxError, app.solve('111111+ 22222 +33333 +55555'))
        # self.assertRaises(RepeatedAnswerError, app.solve, '6*(7 / 12)*3*4')
        self.assertRaises(RepeatedAnswerError, app.solve, '12/(3*4)*6*7')
        self.assertRaises(RepeatedAnswerError, app.solve, '6*7*(12 / (3*4))')
        self.assertRaises(RepeatedAnswerError, app.solve, '(12-3*4)+6*7')
        self.assertEqual(app.get_current_solution_number(), 1)
        app.solve('   （12   +   6  /  3)  *  （7  -   4)')
        self.assertEqual(app.get_current_solution_number(), 2)
        self.assertEqual('本次42点的题目为: 3 4 6 7 12', app.get_current_problem())
        self.assertEqual('有效求解:\n[1] 6*7+(12-3*4)\n[2] (12+6/3)*(7-4)', app.get_current_solved())

        # Stop game
        app.stop()
        self.assertRaises(GameStatusError, app.get_current_problem)
        self.assertRaises(GameStatusError, app.get_current_solved)
        self.assertRaises(GameStatusError, app.get_current_solution_number)
        self.assertRaises(GameStatusError, app.get_total_solution_number)
        self.assertRaises(GameStatusError, app.solve, '123' )
        self.assertRaises(GameStatusError, app.stop)

class TestException(unittest.TestCase):
    def test_exceptions(self):
        self.assertEqual(str(GameStatusError(True)), 'Required status: PLAYING')
        self.assertEqual(str(GameStatusError(False)), 'Required status: NOT PLAYING')
        self.assertEqual(str(WrongAnswerError(40)), '你的结果[40]是错误的')
        self.assertEqual(str(UnsupportedSyntaxError('40')), '你的公式无法识别[40]')
        self.assertEqual(str(UnmatchedNumberError([40, 41, 42])), '你使用的数字[40 41 42]与题目所给的不符')
        self.assertEqual(str(RepeatedAnswerError('1+2+3')), '你的结果与解[1+2+3]重复了')
