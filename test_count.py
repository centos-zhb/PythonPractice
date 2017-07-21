# -*- coding:utf-8 -*-
import unittest
from count import Calculator

class counttest(unittest.TestCase):
    def setUp(self):
        self.cal = Calculator(24,6)

    def tearDown(self):
        pass

    def test_add(self):
        result = self.cal.add()
        self.assertEqual(result,30)

    def test_sub(self):
        result = self.cal.sub()
        self.assertEqual(result,18)

    def test_mul(self):
        result = self.cal.mul()
        self.assertEqual(result,144)

    def test_div(self):
        result = self.cal.div()
        self.assertEqual(result,4)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(counttest("test_add"))
    suite.addTest(counttest("test_sub"))
    suite.addTest(counttest("test_mul"))
    suite.addTest(counttest("test_div"))
    #执行测试
    runner = unittest.TextTestRunner()
    runner.run(suite)