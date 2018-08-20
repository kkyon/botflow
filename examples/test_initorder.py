

class A(object):
    def __init__(self,*args):
        print('int A')


class B(object):

    def __init__(self,*args):
        print('int B')



A(B(''))