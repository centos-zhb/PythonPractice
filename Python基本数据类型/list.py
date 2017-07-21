# -*- coding:utf-8 -*-
'''
1、List写在方括号之间，元素用逗号隔开。
2、和字符串一样，list可以被索引和切片。
3、List可以使用+操作符进行拼接。
4、List中的元素是可以改变的。
'''
list = ['abcd',789,2.23,'runoob',70.2]
tinylist = [123,'runoob']

print(list)             #输出完整列表
print(list[0])          #输出列表第一个元素
print(list[1:3])        #从第二个开始输出到第三个元素
print(list[2:])         #输出从第三个元素开始的所有元素
print(tinylist * 2)     #输出两次列表
print(list + tinylist)  #连接列表

list[2] = 22.3
print(list)