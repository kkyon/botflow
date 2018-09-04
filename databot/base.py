import types
import typing

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def list_included(iq, oq):
    if not isinstance(iq, list):
        iq = [iq]
    if not isinstance(oq, list):
        oq = [oq]

    for q in iq:
        for _oq in oq:
            if q is _oq:
                return True
    return False


class CountRef(object):
    __slots__ = ['count']
    def __init__(self):
        self.count=0

    def incr(self,n=1):
        self.count=self.count+n
        return self.count

    def decr(self):

        self.count=self.count-1

        return self.count