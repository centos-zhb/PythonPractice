#!/usr/bin/python
"""Python传不可变对象实例"""
def ChangeInt(a):
    a = 10
    print(a)

b=2
ChangeInt(b)
print(b)

#传可变对象实例
def changeme(mylist ):
    "修改传入的列表"
    mylist.append([1,2,3,4])
    print("函数内取值： ",mylist)
    return

#调用changme函数
mylist = [10,20,30]
changeme(mylist)
print("函数外取值： ",mylist)