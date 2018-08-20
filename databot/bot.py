
import asyncio
import logging
from collections import namedtuple
from . import flow
import types

class BotInfo(object):
    def __init__(self,q_i,q_o,func_or_cor,o_f):
        self.q_i=q_i
        self.q_o=q_o
        self.cor=func_or_cor
        self.o_f = o_f
        self.stat='INIT'


async def call_wrap(func, param, q):
    logging.debug('task_wrape'+str(type(func))+str(func))
    r_or_c=func(param)
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

    else:
        if asyncio.iscoroutine(r_or_c):
            r=await r_or_c



        else:
            r=r_or_c
        logging.debug('task_wrape call result r' + str(type(r)))
        if isinstance(r,list):
            for i in r:
                await q.put(i)
        #TODO
        # elif isinstance(r,asyncio.Queue):
        #     while r.empty():
        #
        #         await q.put()
        else:
            await q.put(r)


class Bot(object):
    _bots=[]

    @classmethod
    def run(cls):
        bot_nodes=[]
        for b in cls._bots:
            bot_nodes.append(b.cor)
        logging.info('bot number %s',len(cls._bots))
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
        fc = asyncio.ensure_future(f(iq, oq))

        Bot._bots.append(BotInfo(iq, oq, fc, fc))


    @classmethod
    def make_bot(cls,i, o, f):

        async def _make_bot(i_q, o_q, func):
            if isinstance(func, flow.Node):
                await func.node_init()

            is_stop = False
            while True:
                tasks = []

                logging.debug(str(func))
                if is_stop and i_q.empty():
                    logging.debug('%s,stop %s', str(func), is_stop)
                    await o_q.put(StopIteration())

                    if isinstance(func, flow.Node):
                        await func.node_close()

                    break
                data_list = []
                t = await i_q.get()
                data_list.append(t)
                while not i_q.empty():
                    t = i_q.get_nowait()
                    data_list.append(t)

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
            fc = asyncio.ensure_future(_make_bot(i, o, f))

            cls._bots.append(BotInfo(i,o,fc,f))