
import asyncio
import logging
from collections import namedtuple
from . import flow
from . import node
import types
from .config import config
import logging
logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)s:%(message)s', level=logging.INFO)


class BotPerf(object):
    __slots__=['processed_number','func_avr_time','func_max_time','func_min_time']
    def __init__(self):
        self.processed_number=0
        self.func_avr_time=None
        self.func_max_time = None
        self.func_min_time = None


class BotInfo(object):
    __slots__ = ['iq', 'oq', 'futr','task','func','route_zone','pipeline','stoped','perf','parent_count','stoped_count','parents']
    def __init__(self):
        self.iq=None
        self.oq=None
        self.futr = None
        self.task=None
        self.func=None
        self.route_zone=None
        self.pipeline=None
        self.stoped=False
        self.perf=BotPerf()
        self.parent_count=0
        self.stoped_count=0
        self.parents=[]
    def __repr__(self):
        return str(id(self))

async def handle_exception(e, param, iq):
    if config.exception_policy == config.Exception_raise:
        raise e
    elif config.exception_policy == config.Exception_ignore:
        pass
    elif config.exception_policy == config.Exception_retry:
        await iq.put(param)

async def call_wrap(func, param, iq,oq):
    logging.debug('call_wrap'+str(type(func))+str(func))
    try:
        r_or_c=func(param)
    except Exception as e:
        await handle_exception(e, param, iq)
        return
    if isinstance(r_or_c, types.AsyncGeneratorType):
        async def sync_two_source():
            async for i in r_or_c:
                await oq.put(i)

        await asyncio.get_event_loop().create_task(sync_two_source())

    elif isinstance(r_or_c,asyncio.Queue):
        async def sync_two_source():
            while True:
                i=await r_or_c.get()
                await oq.put(i)

        await asyncio.get_event_loop().create_task(sync_two_source())


    elif  isinstance(r_or_c,types.GeneratorType) or isinstance(r_or_c,list):
            r=r_or_c
            for i in r:
                await oq.put(i)
    elif isinstance(r_or_c,types.CoroutineType):

            try:
                r=await r_or_c
                if isinstance(r, types.GeneratorType) or isinstance(r, list):

                    for i in r:
                        await oq.put(i)
                else:
                    await oq.put(r)
            except Exception as e:

                 await handle_exception(e,param,iq)

            #TODO

    else:
            await oq.put(r_or_c)

class PerfMetric(object):
    batch_size = 32
    suspend_time=1
    def __init__(self):
      pass


class BotFrame(object):
    bots=[]

    @classmethod
    def run(cls):
        BotFrame.debug()
        bot_nodes=[]
        for b in cls.bots:
            bot_nodes.append(b.futr)

        logging.info('bot number %s', len(cls.bots))
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*bot_nodes))
    @classmethod

    def get_botinfo(cls):
        task=asyncio.Task.current_task()
        for b in BotFrame.bots:
            if b.futr is task:
                return b

    @classmethod
    def debug(cls):
        for b in cls.bots:

            plist=''
            for p in b.parents:
                plist+=str(id(p))+','

            logging.info('botid %s,pipe:%s,func:%s stoped:%s,parents:%s'%(b,b.pipeline,b.func,b.stoped,plist))
            #
            #
            # if b.iq is not None and not isinstance(b.iq,flow.NullQueue):
            #     logging.info('len of iq:%s' % (b.iq.qsize()))


    @classmethod
    def make_bot_raw(cls,iq,oq,f):
        fu = asyncio.ensure_future(f)
        bi=BotInfo()
        bi.iq=iq
        if not isinstance(oq,list):
            oq=[oq]
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
    def ready_to_stop(self,bi):
        if bi.iq is not None and not bi.iq.empty():
            return False

        for p in bi.parents:
            if p.stoped == False:
                return False
        b=bi
        logging.info('ready_to_stop botid %s' % (b))
        return True

    @classmethod
    def make_bot(cls,i, o, f):

        async def _make_bot(i_q, o_q, func):
            if isinstance(func, node.Node):
                await func.init()
            bi=cls.get_botinfo()

            while True:
                tasks = []


                data_list = await cls.copy_size(i_q)

                for data in data_list:
                    if not isinstance(data, BotControl):
                        task = asyncio.ensure_future(call_wrap(func, data,i_q, o_q))
                        tasks.append(task)
                if len(tasks) != 0:
                    await asyncio.gather(*tasks)

                if BotFrame.ready_to_stop(bi):
                    if isinstance(func, node.Node):
                        await func.close()
                    bi.stoped=True

                    await o_q.put(Retire())

                    break


        if isinstance(f,flow.Route):
            #deligate with route make_bot func
            f.make_route_bot(i, o)

        else:
            fu = asyncio.ensure_future(_make_bot(i, o, f))
            bi=BotInfo()
            bi.iq=i
            bi.oq=[o]
            bi.func=f
            bi.futr=fu

            BotFrame.bots.append(bi)
    @classmethod
    def q_one_to_two_type(self,input_q,main_o_q,inside_q_list,type_list=[object],share=True ):
        async def wrap():
            bi=BotFrame.get_botinfo()
            is_stop=False
            while True:
                item = await input_q.get()



                matched = flow.Route.type_match(item, type_list)
                if matched :
                    for q in inside_q_list:
                        await q.put(item)

                if share==True:
                    await main_o_q.put(item)
                else:
                    if not matched:
                        await main_o_q.put(item)
                    else:
                        pass
                if self.ready_to_stop(bi):
                    bi.stoped=True
                    for q in inside_q_list+[main_o_q]:
                        await q.put(Retire())
                    break




        BotFrame.make_bot_raw(input_q,inside_q_list+[main_o_q],wrap())





class BotControl(object):
    pass


class Retire(BotControl):
    pass

class Suspend(BotControl):
    pass

class Resume(BotControl):
    pass

class ChangeIq(BotControl):

    def __init__(self,iq_num=128):
        self.iq_num=iq_num
