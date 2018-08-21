
import asyncio
import logging
from collections import namedtuple
from . import flow
from . import node
import types

class BotInfo(object):
    __slots__ = ['iq', 'oq', 'futr','task','func','route_zone','pipeline','stat']
    def __init__(self):
        self.iq=None
        self.oq=None
        self.futr = None
        self.task=None
        self.func=None
        self.route_zone=None
        self.pipeline=None
        self.stat='INIT'

suppress_exception=False
async def call_wrap(func, param, q):
    logging.debug('task_wrape'+str(type(func))+str(func))
    try:
        r_or_c=func(param)
    except Exception as e:
        if not suppress_exception:
            raise e
        await q.put(e)
        return
    if isinstance(r_or_c, types.AsyncGeneratorType):
        async def sync_two_source():
            async for i in r_or_c:
                await q.put(i)

        await asyncio.get_event_loop().create_task(sync_two_source())

    elif isinstance(r_or_c,asyncio.Queue):
        async def sync_two_source():
            while True:
                i=await r_or_c.get()
                await q.put(i)

        await asyncio.get_event_loop().create_task(sync_two_source())


    elif  isinstance(r_or_c,types.GeneratorType) or isinstance(r_or_c,list):
            r=r_or_c
            for i in r:
                await q.put(i)
    elif isinstance(r_or_c,types.CoroutineType):

            r=await r_or_c
            await q.put(r)

    else:
            await q.put(r_or_c)

class PerfMetric(object):
    batch_size = 32
    suspend_time=1
    def __init__(self):
      pass


class BotFrame(object):
    bots=[]

    @classmethod
    def run(cls):
        bot_nodes=[]
        for b in cls.bots:
            bot_nodes.append(b.futr)
            print('pipe:%s,func:%s'%(b.pipeline,b.func))
        logging.info('bot number %s', len(cls.bots))
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*bot_nodes))

    def debug(name):
        starttime = None
        count = 0
        call_time = 0

        async def wraper(p):
            nonlocal call_time
            nonlocal count
            call_time = call_time + 1

            count += len(p)
            print("name %s,count %s,call_time: %s %s ,%s" % (name, count, call_time, type(p), len(p)))

            return p

        return wraper


    @classmethod
    def make_bot_raw(cls,iq,oq,f):
        fu = asyncio.ensure_future(f)
        bi=BotInfo()
        bi.iq=iq
        bi.oq=oq
        bi.futr=fu
        bi.func=f


        BotFrame.bots.append(bi)


    @classmethod
    async def copy_size(cls,q):
        data_list=[]
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
            if count >= qsize or count >= PerfMetric.batch_size:
                break
        return data_list

    @classmethod
    def make_bot(cls,i, o, f):

        async def _make_bot(i_q, o_q, func):
            if isinstance(func, node.Node):
                await func.node_init()

            is_stop = False
            while True:
                tasks = []

                logging.debug(str(func))
                if is_stop and i_q.empty():
                    logging.debug('%s,stop %s', str(func), is_stop)
                    await o_q.put(StopIteration())

                    if isinstance(func, node.Node):
                        await func.node_close()

                    break
                data_list = await cls.copy_size(i_q)


                # while not i_q.empty():
                #     t = await i_q.get()
                #     data_list.append(t)

                for data in data_list:
                    if isinstance(data, StopIteration):
                        is_stop = True
                        continue

                    task = asyncio.ensure_future(call_wrap(func, data, o_q))
                    tasks.append(task)
                if len(tasks) != 0:
                    await asyncio.gather(*tasks)

        if isinstance(f,flow.Route):
            #deligate with route make_bot func
            f.make_route_bot(i, o)

        else:
            fu = asyncio.ensure_future(_make_bot(i, o, f))
            bi=BotInfo()
            bi.iq=i
            bi.oq=o
            bi.func=f
            bi.futr=fu

            cls.bots.append(bi)