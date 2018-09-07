import asyncio
from .bdata import Bdata
from .base import Singleton
from .config import config
import logging
import datetime
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
            if isinstance(q,DataQueue):
                logger.info("qid :{},max size:{},qsize:{},high water:{},data:{}".format(id(q),q.maxsize,q.qsize(),q.high_water,type(q)))
            else:
                logger.info("qid :{},type:{}".format(id(q),type(q)))



class DataQueue(asyncio.Queue):
    def __init__(self,maxsize=None,loop=None):


        if maxsize is None:
            maxsize=config.default_queue_max_size

        super().__init__(maxsize=maxsize,loop=None)
        self.qm=QueueManager()
        self.debug = True
        self.high_water = 0
        self.qm.add(self)
        self.put_count=0

        self.start_time=datetime.datetime.now()
        self.speed_limit=config.backpressure_rate_limit
        self.lock=asyncio.Lock()

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
        '''with out any limit ,the max put speed 23200 from list a generator'''
        if not isinstance(item,Bdata):
            e=Exception('not right data'+str(type(item)))
            logger.error(e)
            raise e

        if self.speed_limit !=0:
            self.put_count += 1


            if self.put_count >self.speed_limit*2:
                await self.lock.acquire()
                end = datetime.datetime.now()
                s = (end - self.start_time).total_seconds()
                speed_now = self.put_count / s
                logger.debug(f"q{id(self)} speed now:{speed_now} {s} {self.put_count}")
                if speed_now > (self.speed_limit * 1.1):
                    sleep_time = self.put_count / self.speed_limit - s
                    logger.debug(f"q{id(self)} need to sleep{sleep_time} ")
                    logger.debug(f"start q{id(self)} {datetime.datetime.now()}")
                    self.start_time = datetime.datetime.now()
                    await asyncio.sleep(sleep_time)
                    logger.debug(f"end q{id(self)} {datetime.datetime.now()}")

                else:
                    self.start_time = datetime.datetime.now()
                self.put_count = 0


                self.lock.release()


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