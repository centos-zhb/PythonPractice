# -*- coding:utf-8 -*-
#!/usr/bin/python
import random

def equalseNum(num):  #函数名首字母小写，后面每个单词首字母大写
    if (num == 6):
        print(1)
    else:
        print(0)
num = random.randrange(1,9)  #声明并初始化变量num
print('num= '+str(num))
print(equalseNum(num))