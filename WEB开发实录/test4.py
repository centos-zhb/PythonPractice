# -*- coding:utf-8 -*-
#!/usr/bin/python

class myClass:  #定义一个类myClass
    def myFun(self):  #在类myClass中定义函数myFun()
        num = 12  #在函数myFun()中定义局部变量num
        print('myFun num =' + str(num))
    def myFun2(self):  #在类myClass中定义另一个函数myFun2()
        num = num+1  #在函数myFun2()中调用myFun()函数中的局部变量num，并重新赋值
        print('myFun2 num='+str(num))
    num*=10   #在类myClass中调用myFun()函数中的局部变量num，并重新赋值
    print('myClass num='+str(num))