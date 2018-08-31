import asyncio
import collections
import pickle
from asyncio.queues import PriorityQueue
from databot.bdata import Bdata
import functools

class DataQueue(asyncio.Queue):
    def __init__(self):
        self.put_callback=None
        super().__init__(maxsize=128)

    def set_put_callback(self,f):
        self.put_callback=f

    async def put(self, item):
        if not isinstance(item,Bdata):
            raise Exception('not right data'+str(type(item)))

        r= await super().put(item)
        if self.put_callback is not None:
             asyncio.ensure_future(self.put_callback(item))
        return r


class ListQueue(asyncio.Queue):
    def __init__(self, it):
        self.it = it
        super().__init__()

    def _init(self, maxsize):
        self._queue = collections.deque(self.it)


class GodQueue(asyncio.Queue):

    # |
    # X
    def __init__(self):
        self.last_put = None
        self.ori=0
        self._data =[Bdata(0,ori=self.ori)]
        pass

    def qsize(self):
        return len(self._data)
    def empty(self):
        return len(self._data )==0

    def put_nowait(self, item):
        raise NotImplementedError()

    async def put(self, item):
        raise NotImplementedError()

    async def get(self):
        return self.get_nowait()


    def get_nowait(self):
        d=self._data[0]
        self._data=[]
        return d


class NullQueue(asyncio.Queue):

    # |
    # X
    def __init__(self):
        self.last_put = None
        pass

    def empty(self):
        return False

    def put_nowait(self, item):
        raise NotImplementedError()

    async def put(self, item):
        # do nothing
        self.last_put = item
        await asyncio.sleep(0)

    async def get(self):
        await asyncio.sleep(0, )

    def get_nowait(self):
        raise NotImplementedError()

class CachedQueue(asyncio.Queue):

    # |
    # X
    def __init__(self):
        self.last_put = None
        self.is_load =False
        self.cache=[]
        super().__init__(maxsize=128)

    def abandon(self):
        self.cache=[]

    # def persist(self,filename):
    #     with open(filename) as f:
    #         pickle.dump()
    #
    # def load(self):
    #     pass
    def load_cache(self,cache):
        for item in cache:
            super().put_nowait(item)
        self.cache=cache
    async def get(self):
        return await super().get()

    async   def put(self, item):
        if self.is_load :
            raise Exception('can not put to a loaded queue')
        # do nothing
        self.last_put = item
        await super().put(item)
        self.cache.append(item)
