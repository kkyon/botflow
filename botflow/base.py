
import asyncio
from .config import config
import asyncio
import types
# import uvloop
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

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


async def copy_size( q):
        data_list = []
        t = await q.get()
        data_list.append(t)

        qsize = q.qsize()
        # get branch size without wait.

        count = 0
        while qsize > 0:
            try:
                t = q.get_nowait()
            except asyncio.queues.QueueEmpty:

                break

            data_list.append(t)
            count += 1
            if count >= qsize or count >= config.coroutine_batch_size:
                break
        return data_list


def flatten(d):
    for x in d:
        if hasattr(x, '__iter__') and  isinstance(x, (list,types.GeneratorType)):
            for y in flatten(x):
                yield y
        else:
            yield x



class BotExit(Exception):
    pass


_BOT_LOOP=asyncio.new_event_loop()

def get_loop():
    return _BOT_LOOP
