# 0、a,b为参数。从字符串指针为a的地方开始截取字符，到b的前一个位置（因为不包含b）
var1 = "hello world"
print(var1)

# 1、如果a,b均不填写，默认取全部字符。即，下面这两个打印结果是一样的
print(var1[: ])  # hello world
print(var1)      # hello world

# 2、如果a填写，b不填写（或填写的值大于指针下标），默认从a开始截取，至字符串最后一个位置
print(var1[3: ]) # lo world

# 3、如果a不填写， b填写，默认从0位置开始截取，至b的前一个位置
print(var1[: 8]) # hello wo

# 4、如果a为负数，默认从尾部某一位置，开始向后截取
print(var1[-2: ]) # ld

# 5、如果a>=b, 默认输出为空。
print(var1[3: 3])
print(var1[3: 2])