
import typing

class func(object):

    def __call__(self, s:str):
        return s
def fun(s):
    return s
def only_str(s : str):
    return s

print(typing.get_type_hints(only_str))
s=typing.get_type_hints(only_str)
print(len(s))
print(s.values())

print('callable object')
s=typing.get_type_hints(func.__call__)
print(len(s))
print(s.values())


print(typing.get_type_hints(fun))



from botflow import Pipe,BotFlow


class A:
    pass

class B:
    pass


class C:
    pass

def only_a(data: A):

    assert isinstance(data,A)
    print("i got A")


Pipe(
    [A(),B(),C()],
    only_a,

    print

)

BotFlow.run()