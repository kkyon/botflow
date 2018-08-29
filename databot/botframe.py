import asyncio
from databot import flow
from databot import node
import types
import typing
from databot.config import config
import logging
from collections.abc import Iterable
from graphviz import Graph

logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)s:%(message)s', level=logging.INFO)


class BotPerf(object):
    __slots__ = ['processed_number', 'func_avr_time', 'func_max_time', 'func_min_time']

    def __init__(self):
        self.processed_number = 0
        self.func_avr_time = None
        self.func_max_time = None
        self.func_min_time = None


class BotInfo(object):
    __slots__ = ['id','iq', 'oq', 'futr', 'task', 'func', 'route_zone', 'pipeline', 'stoped', 'perf', 'ep','idle',
                  'parents','flow']

    def __init__(self):
        self.id=0
        self.iq = []
        self.oq = []
        self.futr = None
        self.task = None
        self.func = None
        self.route_zone = None
        self.pipeline = None
        self.stoped = False
        self.idle=True
        self.flow=''
        self.perf = BotPerf()
        self.ep=config.Exception_default
        self.parents = []

    def __repr__(self):
        return str(id(self))


async def handle_exception(e, param, iq,oq):
    if config.exception_policy == config.Exception_raise:
        raise e
    elif config.exception_policy == config.Exception_ignore:
        return
    elif config.exception_policy == config.Exception_pipein:
        await oq.put(e)
    elif config.exception_policy == config.Exception_retry:
        await iq.put(param)
    else:
        raise Exception('undefined exception policy')


async def call_wrap(func, param, iq, oq):
    logging.debug('call_wrap' + str(type(func)) + str(func))
    try:
        r_or_c = func(param)
    except Exception as e:
        await handle_exception(e, param, iq,oq)
        return
    if isinstance(r_or_c, types.AsyncGeneratorType):
        async def sync_two_source():
            async for i in r_or_c:
                await oq.put(i)

        await asyncio.get_event_loop().create_task(sync_two_source())

    elif isinstance(r_or_c, asyncio.Queue):
        async def sync_two_source():
            while True:
                i = await r_or_c.get()
                await oq.put(i)

        await asyncio.get_event_loop().create_task(sync_two_source())

    elif isinstance(r_or_c,(str,typing.Tuple)):
        await oq.put(r_or_c)

   # elif isinstance(r_or_c, types.GeneratorType) or isinstance(r_or_c, list):
    elif isinstance(r_or_c, typing.Iterable) :
        r = r_or_c
        for i in r:
            await oq.put(i)
    elif isinstance(r_or_c, types.CoroutineType):

        try:
            r = await r_or_c
            if isinstance(r, types.GeneratorType) or isinstance(r, list):

                for i in r:
                    await oq.put(i)
            else:
                await oq.put(r)
        except Exception as e:

            await handle_exception(e, param, iq,oq)

        # TODO

    else:
        await oq.put(r_or_c)


class PerfMetric(object):
    batch_size = 32
    suspend_time = 1

    def __init__(self):
        pass


class BotFrame(object):
    bots = []


    @classmethod
    def render(cls,filename):
        from graphviz import Digraph
        f = Digraph(comment=__file__,format='png')
        f.attr('node', shape='circle')
        pipes={}

        for b in BotFrame.bots:
            name=str(b.func).replace('>','').replace('<','')
            name=name.split('.')[-1]
            name = name.split('at')[0]
            f.node(str(id(b)),name)
            bid=str(id(b))
            for p in b.parents:
                pid=str(id(p))
                f.edge(pid,bid)

        f.render(filename,view=True)


    @classmethod
    def run(cls):

        if config.replay_mode:
            try:
                flow.Pipe.restore_for_replay()
            except:
                raise

        BotFrame.debug()
        bot_nodes = []
        for b in cls.bots:
            #if not b.stoped:
            bot_nodes.append(b.futr)

        logging.info('bot number %s', len(cls.bots))
        try:
            asyncio.get_event_loop().run_until_complete(asyncio.gather(*bot_nodes))
        except Exception as e:
            if config.replay_mode:
                flow.Pipe.save_for_replay()
                raise e

            else:
                raise e

    @classmethod
    def get_botinfo_by_id(cls,id):
        for b in BotFrame.bots:
            if b.id == id:
                return b
        return None
    @classmethod
    def get_botinfo(cls) ->BotInfo:
        task = asyncio.Task.current_task()
        for b in BotFrame.bots:
            if b.futr is task:
                return b

    @classmethod
    def type_match(cls, msg, type_list):
        for t in type_list:
            if isinstance(msg, t):
                return True

        return False
    @classmethod
    def debug(cls):
        logging.info('-' * 100)
        for b in cls.bots:

            if not isinstance(b.iq,list):
                b.iq=[b.iq]
            plist = ''
            for p in b.parents:
                plist += 'b_'+str(id(p)) + ','

            oq=''
            for q in b.oq:
                oq += 'q_'+str(id(q)) + ','

            iq=''
            for q in b.iq:
                iq += 'q_' + str(id(q)) + ','


            logging.info('%s,botid %s,pipe:%s,func:%s stoped:%s,parents:%s  ,iq:%s, oq:%s'% (b.id,b, b.pipeline, b.func, b.stoped,plist,iq,oq))
            #
            #
            # if b.iq is not None :
            #     logging.info('len of iq:%s' % (b.iq.qsize()))

    @classmethod
    def make_bot_raw(cls, iq, oq, f):
        fu = asyncio.ensure_future(f)
        bi = BotInfo()
        bi.iq = iq
        if not isinstance(oq, list):
            oq = [oq]
        bi.oq = oq
        bi.futr = fu
        bi.func = f

        BotFrame.bots.append(bi)

    @classmethod
    async def copy_size(cls, q):
        data_list = []
        t = await q.get()
        data_list.append(t)

        qsize = q.qsize()
        # get branch size without wait.

        count = 0
        while qsize > 0:
            try:
                t =  q.get_nowait()
            except asyncio.queues.QueueEmpty:

                break

            data_list.append(t)
            count += 1
            if count >= qsize or count >= PerfMetric.batch_size:
                break
        return data_list

    @classmethod
    def ready_to_stop(self, bi):
        if bi.iq is not None :
            if not isinstance(bi.iq,list):
                raise Exception('')
            for q in bi.iq:
                if  not q.empty():
                    return False

        for p in bi.parents:
            if p.stoped == False:
                return False
        b = bi
        logging.info('ready_to_stop botid %s' % (b))
        return True


    bot_id=0
    @classmethod
    def new_bot_id(cls):
        cls.bot_id+=1
        return cls.bot_id

    @classmethod
    def make_bot(cls, i, o, f):


        async def _make_timer_bot(i_q,o_q,timer):

                count = 0
                bi = BotFrame.get_botinfo()
                while True:
                    if bi.stoped:
                        break
                    count += 1

                    if timer.max_time and timer.max_time < count:
                        break

                    await timer(count)

                    if timer.until is not None and timer.until():
                        break
                    await asyncio.sleep(timer.delay)


                BotFrame.ready_to_stop(bi)
                bi.stoped = True

                await timer(Retire())


        async def _make_loop_bot(i_q, o_q, loop):

                bi = BotFrame.get_botinfo()
                while True:
                    if bi.stoped:
                        break
                    if BotFrame.ready_to_stop(bi) or (len(bi.parents)==0 and i_q.empty()):

                        bi.stoped = True
                        await   loop(Retire())
                        break
                    v=await i_q.get()
                    await loop(v)

        async def _join_input(i_q, o_q, route):

            bi = cls.get_botinfo()

            while True:
                if bi.stoped:
                    break
                tasks = []

                data= await i_q.get()
                bi.idle = False
                if route is None:
                    raise Exception()

                for q in o_q:
                    await q.put(data)

                if BotFrame.ready_to_stop(bi):
                    bi.stoped = True
                    await   q.put(Retire())

                    break
                bi.idle = True
        async def _join_merged(i_q, o_q, route):

            bi = cls.get_botinfo()

            while True:
                if bi.stoped:
                    break

                tasks = []
                for q in i_q:
                    # TODO need get all extension
                    task = q.get()
                    tasks.append(task)

                r = await asyncio.gather(*tasks)

                all_control_signal=True
                for i in r:
                    if not isinstance(i,BotControl):
                        all_control_signal=False

                if all_control_signal:
                    for i in r:
                        await o_q.put(i)


                else:
                    r=tuple(r)
                    await o_q.put(r)
                if BotFrame.ready_to_stop(bi):
                    bi.stoped = True
                    await o_q.put(Retire())

                    break
                bi.idle = True

        async def _route_input(i_q, o_q, route):

            bi = cls.get_botinfo()

            while True:
                tasks = []


                data_list = await cls.copy_size(i_q)
                bi.idle = False
                if route is None:
                    raise Exception()
                for data in data_list:
                    await route(data)
                if BotFrame.ready_to_stop(bi):
                    bi.stoped = True
                    await   route(Retire())

                    break
                bi.idle = True


        def raw_value_wrap(raw_value):

            def _raw_value_wrap(data):
                return raw_value

            return _raw_value_wrap

        async def _make_bot(i_q, o_q, func):
            if isinstance(func, node.Node):
                await func.node_init()



            bi = cls.get_botinfo()

            while True:
                if bi.stoped:
                    break
                tasks = []

                data_list = await cls.copy_size(i_q)
                bi.idle=False
                for data in data_list:
                    if not isinstance(data, BotControl):
                        task = asyncio.ensure_future(call_wrap(func, data, i_q, o_q))
                        tasks.append(task)
                if len(tasks) != 0:
                    await asyncio.gather(*tasks)

                if BotFrame.ready_to_stop(bi):
                    if isinstance(func, node.Node):
                        await func.node_close()
                    bi.stoped = True

                    await o_q.put(Retire())

                    break
                bi.idle = True

        #if not isinstance(f, (list,str, bytes, int, float,types.GeneratorType,Iterable)):
        if not isinstance(f, typing.Callable):
            f = raw_value_wrap(f)

        if isinstance(f,flow.BlockedJoin):
            f.make_route_bot(i,o)

            fu = asyncio.ensure_future(_join_input(i, f.start_q, f))
            bi = BotInfo()
            bi.iq = [i]
            bi.oq = f.start_q
            bi.func = _join_input
            bi.futr = fu
            bi.id=cls.new_bot_id()

            BotFrame.bots.append(bi)

            fu = asyncio.ensure_future(_join_merged(f.tmp_output_q, o, f))
            bi_o = BotInfo()
            bi_o.iq = f.tmp_output_q
            bi_o.oq = [o]
            bi_o.func = _join_merged
            bi_o.futr = fu
            bi_o.id = cls.new_bot_id()

            BotFrame.bots.append(bi_o)
            return [bi,bi_o]



        elif isinstance(f,flow.Timer):
            f.make_route_bot(i,o)
            fu = asyncio.ensure_future(_make_timer_bot(i, o, f))
            bi = BotInfo()
            bi.iq = []
            bi.oq = [o]
            bi.func = f
            bi.futr = fu
            bi.id = cls.new_bot_id()

            BotFrame.bots.append(bi)
            return [bi]


        elif isinstance(f, flow.Loop):
            f.make_route_bot(i,o)
            fu = asyncio.ensure_future(_make_loop_bot(i, o, f))
            bi = BotInfo()
            bi.iq = [i]
            bi.oq = [o]
            bi.func = f
            bi.futr = fu
            bi.id = cls.new_bot_id()

            BotFrame.bots.append(bi)
            return [bi]

        elif isinstance(f, flow.Route):
            # deligate with route make_bot func
            #for output
            f.make_route_bot(i,o)

            #for input

            fu = asyncio.ensure_future(_route_input(i, f.start_q, f))
            bi = BotInfo()
            bi.iq = [i]
            if f.share:
                bi.oq = f.start_q+[o]
            else:
                bi.oq = f.start_q



            bi.func = f
            bi.futr = fu
            bi.id = cls.new_bot_id()

            BotFrame.bots.append(bi)
            return [bi]


        else:
            fu = asyncio.ensure_future(_make_bot(i, o, f))
            bi = BotInfo()
            bi.iq = [i]
            bi.oq = [o]
            bi.func = f
            bi.futr = fu
            bi.id = cls.new_bot_id()
            BotFrame.bots.append(bi)
            return [bi]




class BotControl(object):
    pass


class Retire(BotControl):
    pass


class Suspend(BotControl):
    pass


class Resume(BotControl):
    pass


class ChangeIq(BotControl):

    def __init__(self, iq_num=128):
        self.iq_num = iq_num
