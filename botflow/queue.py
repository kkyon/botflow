import asyncio
from .bdata import Bdata
from .base import Singleton
from .config import config
class QueueManager(object,metaclass=Singleton):

    def __init__(self):
        self.q_list=[]
        self.debug=False

    def add(self,q):
        self.q_list.append(q)

    def debug_print(self):

        print("*"*20,"QueueManager")

        for q in self.q_list:
            if  isinstance(q,DataQueue):
                print("qid :{},size:{},high water:{},data:".format(id(q),q.qsize(),q.high_water,q))
            else:
                print("qid :{},type:{}".format(id(q),type(q)))
        print("*"*20,"QueueManager")


class DataQueue(asyncio.Queue):
    def __init__(self,maxsize=config.queue_max_size):
        qm=QueueManager()
        self.debug = False
        if qm.debug:
            qm.add(self)
            self.debug=True
            self.high_water=0

        self.put_callback=None
        super().__init__(maxsize=maxsize)



    def set_put_callback(self,f):
        self.put_callback=f

    async def put(self, item):
        if not isinstance(item,Bdata):
            raise Exception('not right data'+str(type(item)))

        r= await super().put(item)

        if self.debug:
            if self.qsize()>self.high_water:
                self.high_water=self.qsize()

        if self.put_callback is not None:
             asyncio.ensure_future(self.put_callback(item))
        return r

    async def get(self):

        r=await super().get()
        #r.destroy()
        return r

class NullQueue(asyncio.Queue):

    # |
    # X
    def __init__(self):
        self.last_put = None
        QueueManager().add(self)

    def empty(self):
        return True

    def put_nowait(self, item):
        raise NotImplementedError()

    async def put(self, item):
        # do nothing
        item.destroy()
        del self.last_put
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
        QueueManager().add(self)


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

class ProxyQueue(asyncio.Queue):

    # |
    # X
    def __init__(self, maxsize=0, *, loop=None):
        super().__init__(maxsize=maxsize,loop=loop)
        self._q=DataQueue()


    def set_q(self,q):
        #it will make the data lose
        self._q=q
    def empty(self):
        return self._q.empty()

    def put_nowait(self, item):
        return self._q.put_nowait(item)

    async def put(self, item):
        return await self._q.put(item)

    async def get(self):
        return await self._q.get()

    def get_nowait(self):
        return self._q.get_nowait()