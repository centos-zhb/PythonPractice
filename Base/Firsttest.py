class FirstTest:
    def __init__(self,name):
        self._name = name
    def SayFirst(self):
        print("Hello {0}".format(self._name))
F = FirstTest("CNBlogs")
F.SayFirst()