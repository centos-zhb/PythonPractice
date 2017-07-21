class FirstTest:
    def __init__(self,name):
        self._name = name
    def SayFirst(self):
        print("Hello {0}".format(self._name))

class SecondTest(FirstTest):
    def __init__(self,name):
        FirstTest.__init__(self,name)
    def SaySecond(self):
        print("Good {0}".format(self._name))

S = SecondTest("CNBlogs");
S.SayFirst()
S.SaySecond();