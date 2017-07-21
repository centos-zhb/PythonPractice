#coding=utf-8

age = int(input("输入你家dog的年纪："))
print(" ")
if age < 0:
    print("Are you kidding me?")
elif age==1:
    print("相当于人类14岁")
elif age==2:
    print("相当于人类22岁")
else:
    human = 22 + (age-2)*5
    print("对应人类的年纪是：",human)

input("点击enter推出")