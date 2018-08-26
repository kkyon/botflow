import asyncio
import logging
from collections import namedtuple
from databot import flow
from databot import node
import types
from databot.config import config
import logging
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
    __slots__ = ['iq', 'oq', 'futr', 'task', 'func', 'route_zone', 'pipeline', 'stoped', 'perf', 'parent_count','idle',
                 'stoped_count', 'parents']

    def __init__(self):
        self.iq = None
        self.oq = None
        self.futr = None
        self.task = None
        self.func = None
        self.route_zone = None
        self.pipeline = None
        self.stoped = False
        self.idle=True
        self.perf = BotPerf()
        self.parent_count = 0
        self.stoped_count = 0
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


    elif isinstance(r_or_c, types.GeneratorType) or isinstance(r_or_c, list):
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
        # for b in BotFrame.bots:
        #     name=str(b.func).replace('>','').replace('<','')
        #     name=name.split('.')[-1]
        #     name = name.split('at')[0]
        #     f.node(str(id(b)),name)
        #     for q in b.iq:
        #         if q not in pipes:
        #             pipes[q]=['0','0']
        #         pipes[q][1]=str(id(b))
        #     for q in b.oq:
        #         if q not in pipes:
        #             pipes[q]=['0','0']
        #         pipes[q][0] = str(id(b))
        #
        # for k,v in pipes.items():
        #     if v[0]!='0' and v[1]!='0':
        #         f.edge(v[0],v[1])
        # f.render(filename,view=True)

    @classmethod
    def run(cls):
        BotFrame.debug()
        bot_nodes = []
        for b in cls.bots:
            bot_nodes.append(b.futr)

        logging.info('bot number %s', len(cls.bots))
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*bot_nodes))

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


            logging.info('botid %s,pipe:%s,func:%s stoped:%s,parents:%s  ,iq:%s, oq:%s'% (b, b.pipeline, b.func, b.stoped,plist,iq,oq))
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

    @classmethod
    def make_bot(cls, i, o, f):


        async def _make_timer_bot(i_q,o_q,timer):

                count = 0
                bi = BotFrame.get_botinfo()
                while True:
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
                    if BotFrame.ready_to_stop(bi) or (len(bi.parents)==0 and i_q.empty()):

                        bi.stoped = True
                        await   loop(Retire())
                        break
                    v=await i_q.get()
                    await loop(v)

        async def _join_input(i_q, o_q, route):

            bi = cls.get_botinfo()

            while True:
                tasks = []

                data= await i_q.get()
                bi.idle = False
                if route is None:
                    raise Exception()

                for q in o_q:
                    await q.put(data)

                if BotFrame.ready_to_stop(bi):
                    bi.stoped = True
                    await   route(Retire())

                    break
                bi.idle = True
        async def _join_merged(i_q, o_q, route):

            bi = cls.get_botinfo()
            bi.iq = i_q
            while True:

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





        async def _make_bot(i_q, o_q, func):
            if isinstance(func, node.Node):
                await func.node_init()
            bi = cls.get_botinfo()

            while True:
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


        if isinstance(f,flow.BlockedJoin):
            f.make_route_bot(i,o)

            fu = asyncio.ensure_future(_join_input(i, f.start_q, f))
            bi = BotInfo()
            bi.iq = [i]
            bi.oq = f.start_q
            bi.func = _join_input
            bi.futr = fu

            BotFrame.bots.append(bi)

            fu = asyncio.ensure_future(_join_merged(f.tmp_output_q, o, f))
            bi = BotInfo()
            bi.iq = f.tmp_output_q
            bi.oq = [o]
            bi.func = _join_merged
            bi.futr = fu

            BotFrame.bots.append(bi)




        elif isinstance(f,flow.Timer):
            f.make_route_bot(i,o)
            fu = asyncio.ensure_future(_make_timer_bot(i, o, f))
            bi = BotInfo()
            bi.iq = []
            bi.oq = [o]
            bi.func = f
            bi.futr = fu

            BotFrame.bots.append(bi)


        elif isinstance(f, flow.Loop):
            f.make_route_bot(i,o)
            fu = asyncio.ensure_future(_make_loop_bot(i, o, f))
            bi = BotInfo()
            bi.iq = [i]
            bi.oq = [o]
            bi.func = f
            bi.futr = fu

            BotFrame.bots.append(bi)

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

            BotFrame.bots.append(bi)
            return bi


        else:
            fu = asyncio.ensure_future(_make_bot(i, o, f))
            bi = BotInfo()
            bi.iq = [i]
            bi.oq = [o]
            bi.func = f
            bi.futr = fu

            BotFrame.bots.append(bi)
            return bi

    @classmethod
    def q_one_to_two_type(self, input_q, main_o_q, inside_q_list, type_list=[object], share=True):
        async def wrap():
            bi = BotFrame.get_botinfo()
            is_stop = False
            while True:
                item = await input_q.get()

                matched = flow.Route.type_match(item, type_list)
                if matched:
                    for q in inside_q_list:
                        await q.put(item)

                if share == True:
                    await main_o_q.put(item)
                else:
                    if not matched:
                        await main_o_q.put(item)
                    else:
                        pass
                if self.ready_to_stop(bi):
                    bi.stoped = True
                    for q in inside_q_list + [main_o_q]:
                        await q.put(Retire())
                    break

        BotFrame.make_bot_raw(input_q, inside_q_list + [main_o_q], wrap())


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
