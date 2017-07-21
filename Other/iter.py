#!/usr/bin/env python
# 迭代器与生成器
import sys

list=[1,2,3,4,5,6]
it = iter(list) #创建迭代器对象
#for x in it:
#   print(x,end=" ")
while True:
    try:
        print(next(it))
    except StopIteration:
        sys.exit()