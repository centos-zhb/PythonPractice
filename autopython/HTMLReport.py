# -*- coding:utf-8 -*-
import unittest
import HTMLTestRunner
import autopython.baidu

testunit = unittest.TestSuite()

#将测试用例加入到测试容器（套件）中
testunit.addTest(unittest.makeSuite(autopython.baidu.Baidu))

#执行测试套件
runner = unittest.TextTestRunner()
runner.run(testunit)

# #定义报告存放路径，支持相对路径
# filename = 'D:\\testfile\\HTMLReport\\result.html'
# fp = file(filename,'wb')