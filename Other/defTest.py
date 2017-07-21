#!/usr/bin/python
"""计算面积函数"""

def area(width,height):
    return width*height

def print_welcome(name):
    print("Welcome",name)

def printme(str):
    "打印任何传入的字符串"
    print(str)
    return

print_welcome("Runoob")
w = 4
h = 5
print("width=",w,"height=",h,"area=",area(w,h))
#调用函数
printme("我要调用用户自定义函数！")
printme("再调用一次函数")