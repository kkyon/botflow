import asyncio
from .bdata import Bdata
from .base import Singleton,get_loop
from .config import config
import logging
import datetime
import collections
logger = logging.getLogger(__name__)

class QueueManager(object,metaclass=Singleton):

    def __init__(self):
        self.q_list=[]
        self._dev_mode=False



    def reset(self):
        self.q_list=[]

    def add(self,q):

        logger.debug(
            "QM add q_{},max size:{}".format(id(q), q.maxsize))
        self.q_list.append(q)

    def debug_print(self):


        for q in self.q_list:
            if isinstance(q,DataQueue):
                logger.info("q_{},max size:{},qsize:{},high water:{},data:{}".format(id(q),q.maxsize,q.qsize(),q.high_water,type(q)))
            else:
                logger.info("q_{},type:{}".format(id(q),type(q)))

    def dev_mode(self):
        self._dev_mode=True

class DataQueue(asyncio.Queue):
    def __init__(self,maxsize=None,loop=None):


        if maxsize is None:
            maxsize=config.default_queue_max_size

        super().__init__(maxsize=maxsize,loop=get_loop())
        self.qm=QueueManager()
        self.debug = True
        self.high_water = 0
        self.qm.add(self)
        self.put_count=0
        self.get_count=0

        self.start_time=datetime.datetime.now()
        self.speed_limit=config.backpressure_rate_limit
        self.lock=asyncio.Lock()

        self.put_callback=None




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
                logger.debug(f"q_{id(self)} speed now:{speed_now} {s} {self.put_count}")
                if speed_now > (self.speed_limit * 1.1):
                    sleep_time = self.put_count / self.speed_limit - s
                    logger.debug(f"q_{id(self)} need to sleep{sleep_time} ")
                    logger.debug(f"start q_{id(self)} {datetime.datetime.now()}")
                    self.start_time = datetime.datetime.now()
                    await asyncio.sleep(sleep_time)
                    logger.debug(f"end q_{id(self)} {datetime.datetime.now()}")

                else:
                    self.start_time = datetime.datetime.now()
                self.put_count = 0


                self.lock.release()


        r= await super().put(item)

        if self.debug:
            if self.qsize()>self.high_water:
                self.high_water=self.qsize()

        # if self.put_callback is not None:
             # asyncio.ensure_future(self.put_callback(item))
        return r

    def __repr__(self):
        return "{}({})".format(self.__class__,id(self))


    def __str__(self):
        return "{}({})".format(self.__class__,id(self))

    async def get(self):

        r=await super().get()
        #r.destroy()
        return r

    async def get_by(self,ori):
        while True:
            await self.readable()
            item=self._queue[-1]
            if item.ori == ori:
                return self._queue.popleft()


    async def readable(self):
        while self.empty():
            getter = self._loop.create_future()
            self._getters.append(getter)
            try:
                await getter
            except:
                getter.cancel()  # Just in case getter is not done yet.

                try:
                    self._getters.remove(getter)
                except ValueError:
                    pass

                if not self.empty() and not getter.cancelled():
                    # We were woken up by put_nowait(), but can't take
                    # the call.  Wake up the next in line.
                    self._wakeup_next(self._getters)
                raise

        return


class ConditionalQueue:


    def __init__(self, maxsize=0, *, loop=None):

        self.qm = QueueManager()

        self._loop =get_loop()

        self._maxsize = maxsize

        # Futures.
        self._inernel_getters = {} #collections.deque()
        # Futures.
        self._putters = collections.deque()
#        self._unfinished_tasks = 0
#        self._finished = asyncio.Lock.Event(loop=self._loop)
#        self._finished.set()
        self._init(maxsize)

        self.debug = True
        self.high_water = 0
        self.qm.add(self)
        self.put_count=0

    # These three are overridable in subclasses.
    @property
    def _getters(self):
        r=[]
        for k,v in self._inernel_getters.items():
            r.extend(v)
        return r

    def _init(self, maxsize):
        self._queue = {} #collections.deque()
    def _init_dict(self,ori):
        if ori not in self._inernel_getters:
            self._inernel_getters[ori]=collections.deque()

        if ori not in self._queue:
            self._queue[ori]=collections.deque()

    def clean(self,ori):
        del self._inernel_getters[ori]
        del self._queue[ori]


    def _get(self,ori):
        return self._queue[ori].popleft()



    def _put(self, item):

        self._queue[item.ori].append(item)

    # End of the overridable methods.

    def _wakeup_next(self, waiters):
        # Wake up the next waiter (if any) that isn't cancelled.
        while waiters:
            waiter = waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)
                break

    def __repr__(self):
        return '<{} at {:#x} {}>'.format(
            type(self).__name__, id(self), self._format())

    def __str__(self):
        return '<{} {}>'.format(type(self).__name__, self._format())

    def _format(self):
        result = 'maxsize={!r}'.format(self._maxsize)
        if getattr(self, '_queue', None):
            result += ' _queue={!r}'.format(list(self._queue))
        if self._inernel_getters:
            result += ' _getters[{}]'.format(len(self._inernel_getters))
        if self._putters:
            result += ' _putters[{}]'.format(len(self._putters))
        if self._unfinished_tasks:
            result += ' tasks={}'.format(self._unfinished_tasks)
        return result

    def qsize(self):
        """Number of items in the queue."""
        size=0
        for k,v in self._queue.items():
            size+=len(v)
        return size

    @property
    def maxsize(self):
        """Number of items allowed in the queue."""
        return self._maxsize

    def empty(self,ori=None):
        """Return True if the queue is empty, False otherwise."""
        if ori:
            return not self._queue[ori]
        else:
            for k,v in self._queue.items():
                if len(v) >0:
                    return False
            return True

    def full(self):
        """Return True if there are maxsize items in the queue.

        Note: if the Queue was initialized with maxsize=0 (the default),
        then full() is never True.
        """
        if self._maxsize <= 0:
            return False
        else:
            return self.qsize() >= self._maxsize


    async def put(self, item):
        """Put an item into the queue.

        Put an item into the queue. If the queue is full, wait until a free
        slot is available before adding item.

        This method is a coroutine.
        """
        self._init_dict(item.ori)
        while self.full():
            putter = self._loop.create_future()
            self._putters.append(putter)
            try:
                await putter
            except:
                putter.cancel()  # Just in case putter is not done yet.
                if not self.full() and not putter.cancelled():
                    # We were woken up by get_nowait(), but can't take
                    # the call.  Wake up the next in line.
                    self._wakeup_next(self._putters[item.ori])
                raise
        return self.put_nowait(item)

    def put_nowait(self, item):
        """Put an item into the queue without blocking.

        If no free slot is immediately available, raise QueueFull.
        """
        if self.full():
            raise asyncio.QueueFull
        self._put(item)
        # self._unfinished_tasks += 1
        # self._finished.clear()
        self._wakeup_next(self._inernel_getters[item.ori])

    async def readable(self,ori):

        while self.empty(ori):
            getter = self._loop.create_future()
            self._inernel_getters[ori].append(getter)
            try:
                await getter
            except:
                getter.cancel()  # Just in case getter is not done yet.

                try:
                    self._inernel_getters[ori].remove(getter)
                except ValueError:
                    pass

                if not self.empty(ori) and not getter.cancelled():
                    # We were woken up by put_nowait(), but can't take
                    # the call.  Wake up the next in line.
                    self._wakeup_next(self._inernel_getters[ori])
                raise


    async def get_by(self,ori):
        """Remove and return an item from the queue.

        If queue is empty, wait until an item is available.

        This method is a coroutine.
        """
        self._init_dict(ori)
        await self.readable(ori)
        return self.get_nowait(ori)

    def get_nowait(self,ori):
        """Remove and return an item from the queue.

        Return an item if one is immediately available, else raise QueueEmpty.
        """
        if self.empty(ori):
            raise asyncio.QueueEmpty
        item = self._get(ori)
        self._wakeup_next(self._putters)
        return item






class SinkQueue(asyncio.Queue):

    # |
    # X
    def __init__(self):
        super().__init__(loop=get_loop())
        self.last_put = None
        self.qm=QueueManager()
        self.qm.add(self)
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
        if self.qm._dev_mode==True:
            if isinstance(item.data,list):
                max_len=3
                print("-----Output a list len %d , first %d data:---"%(len(item.data),max_len))
                for i,v in enumerate(item.data):
                    if i >max_len:
                        break

                    print("Sink[%d]: %s"%(i,v))
            else:
                print("Sink:",item.data)

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
        super().__init__(maxsize=128,loop=get_loop())
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
    def __init__(self, q,maxsize=0, loop=None):
        super().__init__(maxsize=maxsize,loop=loop)
        self._q=q


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

    async def get_by(self,ori):
        return await self._q.get_by(ori)
    def clean(self,ori):
        return self._q.clean(ori)
    def get_nowait(self):
        return self._q.get_nowait()