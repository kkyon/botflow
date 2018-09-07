import asyncio
from .bdata import Bdata
from .base import Singleton
from .config import config
import logging

logger = logging.getLogger(__name__)

class QueueManager(object,metaclass=Singleton):

    def __init__(self):
        self.q_list=[]


    def add(self,q):

        logger.debug(
            "QM add qid :{},max size:{}".format(id(q), q.maxsize))
        self.q_list.append(q)

    def debug_print(self):


        for q in self.q_list:
            if  isinstance(q,DataQueue):
                logger.debug("qid :{},max size:{},qsize:{},high water:{},data:{}".format(id(q),q.maxsize,q.qsize(),q.high_water,type(q)))
            else:
                logger.debug("qid :{},type:{}".format(id(q),type(q)))



class DataQueue(asyncio.Queue):
    def __init__(self,maxsize=None,loop=None):


        if maxsize is None:
            maxsize=config.default_queue_max_size

        super().__init__(maxsize=maxsize,loop=None)
        self.qm=QueueManager()
        self.debug = False
        self.high_water = 0
        #logging.info("debug %s %s",self.debug,self.qm.debug)
        if logger.level == logging.DEBUG:
            self.qm.add(self)
            self.debug = True


        self.put_callback=None


    async def readable(self):
        pass
        #TODO

    async def writable(self):
        pass
        #TODO

    def set_put_callback(self,f):
        self.put_callback=f

    async def put(self, item):
        if not isinstance(item,Bdata):
            e=Exception('not right data'+str(type(item)))
            logger.error(e)
            raise e

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
        super().__init__()
        self.last_put = None
        QueueManager().add(self)
        self._maxsize=0
    def empty(self):
        return True
    def maxsize(self):
        return 0
    def qsize(self):
        return 0

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
    def __init__(self, maxsize=0, loop=None):
        super().__init__(maxsize=maxsize,loop=loop)
        self._q=DataQueue(maxsize=maxsize,loop=loop)


    def set_q(self,q):
        #it will make the data lose
        self._q=q
    def empty(self):
        return self._q.empty()
    def maxsize(self):
        return self._q.maxsize
    def qsize(self):
        return self._q.qsize()
    def put_nowait(self, item):
        return self._q.put_nowait(item)

    async def put(self, item):
        return await self._q.put(item)

    async def get(self):
        return await self._q.get()

    def get_nowait(self):
        return self._q.get_nowait()