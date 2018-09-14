import asyncio
from .config import config
import logging
from .base import Singleton, list_included,get_loop

from .base import copy_size
from .functionbase import Function
from .bdata import Bdata
from .queue import SinkQueue
import typing, types

logger=logging.getLogger(__name__)
from .base import BotExit
import datetime


class BotPerf(object):
    __slots__ = ['processed_number', 'func_avr_time', 'func_max_time', 'func_min_time']

    def __init__(self):
        self.processed_number = 0
        self.func_avr_time = None
        self.func_max_time = None
        self.func_min_time = None


class BotInfo(object):
    __slots__ = ['id', 'iq', 'oq', 'func', 'route_zone', 'pipeline', 'stoped', 'perf', 'ep', 'idle',
                 'parents', 'flow', "main_coro", "main_task", "sub_task", "sub_coro"]

    def __init__(self):
        self.id = 0
        self.iq = []
        self.oq = []
        self.main_coro = None
        self.main_task = None
        self.sub_task = set()
        self.sub_coro = set()
        self.func = None
        self.route_zone = None
        self.pipeline = None
        self.stoped = False
        self.idle = True
        self.flow = ''
        self.perf = BotPerf()
        self.ep = config.Exception_default
        self.parents = []

    def __repr__(self):
        return " id {} ,func {} stoped {} idle {} tasks{}".format(str(id(self)), self.func, self.stoped, self.idle,
                                                                  len(self.sub_task))


class BotManager(object, metaclass=Singleton):

    def __init__(self):
        self._bots = []
        self._pipes = set()
        self.bot_id = 0
        self.loop=get_loop()


    def rest(self):
        self._bots = []
        self._pipes = set()
        self.bot_id = 0

    def get_pipes(self):
        return self._pipes

    @classmethod
    def ready_to_stop(cls, bi):
        if bi.iq is not None:
            if not isinstance(bi.iq, list):
                raise Exception('')
            for q in bi.iq:
                if not q.empty():
                    return False

        for p in bi.parents:
            if p.stoped == False:
                return False
        b = bi
        logger.info('ready_to_stop botid %s' % (b))
        return True

    def new_bot_id(self):
        self.bot_id += 1
        return self.bot_id
    def remove_by_pipe(self,pipe):

        self._bots = [ b for b  in self._bots if b.pipeline != pipe ]




    def add_pipes(self, pipe):
        self._pipes.add(pipe)

    def add_bot(self, bi):
        if bi.id == 0:
            bi.id = self.new_bot_id()
        self._bots.append(bi)

    def get_bots_bypipe(self, pipe):
        result = []
        for b in self._bots:
            if b.pipeline == pipe:
                result.append(b)

        return result

    def make_bot_flowgraph(self, pipe):
        for bot in self.get_bots_bypipe(pipe):

            count = 0
            for bot_o in self.get_bots_bypipe(pipe):

                for q in bot_o.oq:
                    if list_included(bot.iq, q):
                        bot.parents.append(bot_o)

    def bots_size(self):
        return len(self._bots)

    def get_bots(self):
        return self._bots

    def get_reader_id_by_q(self, q):
        ids = []
        for b in self._bots:
            if list_included(q, b.iq):
                ids.append(b.id)

        return ids

    def get_botinfo_by_id(self, id):
        for b in self._bots:
            if b.id == id:
                return b
        return None

    def get_all_q(self):
        qs = set()
        for b in self._bots:
            for q in b.iq + b.oq:
                if not isinstance(q, SinkQueue):
                    qs.add(q)

        return qs

    def get_botinfo_current_task(self) -> BotInfo:
        task = asyncio.Task.current_task()
        for b in self._bots:
            if b.main_task is task or task in b.sub_task:
                return b

    # def make_bot_raw(self, iq, oq, f, fu):
    #
    #     bi = BotInfo()
    #     bi.iq = iq
    #     if not isinstance(oq, list):
    #         oq = [oq]
    #     bi.oq = oq
    #     bi.futr = fu
    #     bi.func = f

    # self._bots.append(bi)

    def debug_print(self):
        logger.info('-' * 50)
        for b in self._bots:

            if not isinstance(b.iq, list):
                b.iq = [b.iq]
            plist = ''
            for p in b.parents:
                plist += 'b_' + str(id(p)) + ','

            oq = ''
            for q in b.oq:
                oq += 'q_' + str(id(q)) + ','

            iq = ''
            for q in b.iq:
                iq += 'q_' + str(id(q)) + ','

            logger.info('%s,botid %s,pipe:%s,func:%s stoped:%s,parents:%s  ,iq:%s, oq:%s' % (
                b.id, b, b.pipeline, b.func, b.stoped, plist, iq, oq))

        logger.info('-' * 50)
        for b in self._bots:
            logger.info(b)
            #
            #


class PerfMetric(object):
    batch_size = 128
    suspend_time = 1

    def __init__(self):
        pass


async def handle_exception(e, bdata, iq, oq):
    if config.exception_policy == config.Exception_raise:
        raise e
    elif config.exception_policy == config.Exception_ignore:
        return
    elif config.exception_policy == config.Exception_pipein:
        await oq.put(Bdata(e, ori=bdata.ori))
    elif config.exception_policy == config.Exception_retry:
        await iq.put(bdata)
    else:
        raise Exception('undefined exception policy')


def filter_out(data):
    if data is None or data == []:
        return True
    return False


async def call_wrap(func, bdata, iq, oq, raw_bdata=False):
    logger.debug('call_wrap' + str(type(func)) + str(func))

    if raw_bdata:
        param = bdata

    else:
        param = bdata.data

    ori = bdata.ori

    if hasattr(func, 'boost_type'):
        loop = get_loop()
        r_or_c = await loop.run_in_executor(None, func, param)

    else:
        try:
            r_or_c = func(param)
            if filter_out(r_or_c):
                return
        except Exception as e:
            await handle_exception(e, bdata, iq, oq)

            return

    # if isinstance(r_or_c,(str,typing.Tuple,typing.Dict)):
    #     await oq.put(Bdata(r_or_c,ori=ori))

    # elif isinstance(r_or_c, types.GeneratorType) or isinstance(r_or_c, list):
    if isinstance(r_or_c, types.GeneratorType):
        r = r_or_c
        for i in r:
            await oq.put(Bdata(i, ori=ori))
    elif isinstance(r_or_c, types.CoroutineType):

        try:
            r = await r_or_c
            if isinstance(r, types.GeneratorType):

                for i in r:
                    await oq.put(Bdata(i, ori=ori))
            else:
                if filter_out(r):
                    return

                await oq.put(Bdata(r, ori=ori))
        except Exception as e:

            await handle_exception(e, bdata, iq, oq)

        # TODO

    else:
        await oq.put(Bdata(r_or_c, ori=ori))







def raw_value_wrap(message):
    def _raw_value_wrap(v):

        # elif isinstance(r_or_c, types.GeneratorType) or isinstance(r_or_c, list):
        if isinstance(message, typing.Iterable) and (not isinstance(message, (str, dict, tuple))):

            for i in message:
                yield i

        else:

            yield message

    return _raw_value_wrap


async def wrap_sync_async_call(f, data):
    r = f(data)
    if isinstance(r, typing.Coroutine):
        r = await r

    return r


class BotBase(object):

    def __init__(self):

        self.bi = None
        self.coro_list = set()
        self.tasks = []
        self.input_q = None
        self.output_q = None
        self.consumed_count=0
        self.produced_count=0
        self.start_time=datetime.datetime.now()
        self.speed_limit=100
        self.lock=asyncio.Lock()

    # def pre_hook(self):
    # def post_hook(self):
    # def stop(self):

    async def pre_hook(self):
        pass

    async def post_hook(self):
        pass

    def check_stop(self):
        return BotManager.ready_to_stop(self.bi)

    async def main_loop(self):
        await self.pre_hook()
        while True:

            if self.bi.stoped:
                break

            try:

                await self.main_logic()

                # if self.produced_count > 100:
                #         await self.lock.acquire()
                #         end = datetime.datetime.now()
                #         s = (end - self.start_time).total_seconds()
                #         speed_now = self.produced_count / s
                #         if speed_now > (self.speed_limit * 1.1):
                #             sleep_time = self.produced_count / self.speed_limit - s
                #             logger.info(f"{self.func} need to sleep{sleep_time} speed{speed_now} {s} {self.produced_count}")
                #             #await asyncio.sleep(sleep_time)
                #
                #
                #         self.produced_count = 0
                #         self.start_time = datetime.datetime.now()
                #
                #         self.lock.release()

            except BotExit:
                logger.debug("bot_{} exit".format(id(self)))
                break
            except:
                raise
            self.bi.idle = True
            # if self.check_stop():
            #     self.bi.stoped = True
            #
            #     break
        # if self.output_q is not None:
        #     await self.output_q.put(Bdata.make_Retire())

        self.bi.idle = True
        self.bi.stoped = True

        await self.post_hook()

    async def get_data_list(self):
        return await copy_size(self.input_q)

    async def main_logic(self):

        data_list = await self.get_data_list()

        self.bi.idle = False

        tasks = []
        for data in data_list:
            # if not data.is_BotControl():


            coro = self.create_coro(data)
            self.bi.sub_coro.add(coro)
            task = asyncio.ensure_future(coro)
            self.bi.sub_task.add(task)
            tasks.append(task)

        if len(tasks) != 0:
            await asyncio.gather(*tasks)

        for t in tasks:
            self.bi.sub_coro.remove(t._coro)
            self.bi.sub_task.remove(t)
