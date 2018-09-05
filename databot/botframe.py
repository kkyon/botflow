import asyncio
from . import route
import databot.nodebase as node
import typing
import types
from .config import config
import logging
from databot.bdata import Bdata
from .botbase import BotManager, BotInfo,raw_value_wrap
from .bot import CallableBot,RoutOutBot,RoutInBot,TimerBot

logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)s:%(message)s', level=logging.INFO)



#
# async def _make_timer_bot(i_q, o_q, timer):
#     count = 0
#     bi = BotManager().get_botinfo_current_task()
#     while True:
#         if bi.stoped:
#             break
#         count += 1
#
#         if timer.max_time and timer.max_time < count:
#             break
#
#         await o_q.put(Bdata.make_Bdata_zori(count))
#
#         if timer.until is not None and timer.until():
#             break
#         await asyncio.sleep(timer.delay)
#
#     bi.stoped = True
#
#     await o_q.put(Bdata.make_Retire())
#
#
# async def _route_input(i_q, route):
#     bi = BotManager().get_botinfo_current_task()
#
#     while True:
#
#         if bi.stoped:
#             break
#
#         bdata_list = await cls.copy_size(i_q)
#         # data = await i_q.get()
#         bi.idle = False
#         if route is None:
#             raise Exception()
#
#         tasks = []
#         for bdata in bdata_list:
#             task = asyncio.ensure_future(route.route_in(bdata))
#             tasks.append(task)
#
#         if len(tasks) != 0:
#             await asyncio.gather(*tasks)
#
#         for bdata in bdata_list:
#             bdata.destroy()
#
#         if BotFrame.ready_to_stop(bi):
#             bi.stoped = True
#             await   route.route_in(Bdata.make_Retire())
#
#             break
#         bi.idle = True
#
#
# async def _route_output(oq, route):
#     bi = BotManager().get_botinfo_current_task()
#
#     while True:
#
#         if bi.stoped:
#             break
#
#         bi.idle = False
#         if route is None:
#             raise Exception()
#
#         r = await route.route_out()
#         r.incr()
#         await oq.put(r)
#
#         if BotFrame.ready_to_stop(bi):
#             bi.stoped = True
#             await   route.route_in(Bdata.make_Retire())
#
#             break
#         bi.idle = True
#
#
# async def _make_bot(i_q, o_q, func):
#     if isinstance(func, node.Node):
#         await func.node_init()
#         raw_bdata = func.raw_bdata
#
#     else:
#         raw_bdata = False
#
#     bi = BotManager().get_botinfo_current_task()
#
#     while True:
#
#         if bi.stoped:
#             break
#         tasks = []
#
#         data_list = await cls.copy_size(i_q)
#         bi.idle = False
#         for data in data_list:
#             if not data.is_BotControl():
#                 fut = call_wrap(func, data, i_q, o_q, raw_bdata=raw_bdata)
#                 bi.task.add(fut)
#                 task = asyncio.ensure_future(fut)
#                 tasks.append(task)
#
#         if len(tasks) != 0:
#             await asyncio.gather(*tasks)
#
#         for data in data_list:
#             data.destroy()
#         if BotFrame.ready_to_stop(bi):
#             if isinstance(func, node.Node):
#                 await func.node_close()
#             bi.stoped = True
#
#             await o_q.put(Bdata.make_Retire())
#
#             break
#         bi.idle = True
#


class BotFrame(object):

    @classmethod
    def render(cls, filename):
        from graphviz import Digraph
        f = Digraph(comment=__file__, format='png')
        f.attr('node', shape='circle')

        bots = BotManager().get_bots()
        for idx, b in enumerate(bots):
            name = str(b.func).replace('>', '').replace('<', '')
            name = name.split('.')[-1]
            name = name.split('at')[0]
            name = "(%d)" % (idx) + name
            f.node(str(id(b)), name)
            bid = str(id(b))
            for p in b.parents:
                pid = str(id(p))
                f.edge(pid, bid)

        f.render(filename, view=True)

    @classmethod
    def run(cls):

        if config.replay_mode:
            try:
                route.Pipe.restore_for_replay()
            except:
                raise

        bot_nodes = []
        bots = BotManager().get_bots()
        for b in bots:
            # if not b.stoped:
            if b.futr is not None:
                bot_nodes.append(b.futr)

        logging.info('bot number %s', len(bots))
        try:
            asyncio.get_event_loop().run_until_complete(asyncio.gather(*bot_nodes))
        except Exception as e:
            if config.replay_mode:
                route.Pipe.save_for_replay()
                raise e

            else:
                raise e

    @classmethod


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
        logging.info('ready_to_stop botid %s' % (b))
        return True

    @classmethod
    def make_bot(cls, i, o, f):



        if not isinstance(f, typing.Callable):
            f = raw_value_wrap(f)

        if isinstance(f, route.Timer):
            f.make_route_bot(i,o)

            tb=TimerBot(i,o,f)
            bi=tb.make_botinfo()
            BotManager().add_bot(bi)
            #fu = asyncio.ensure_future(_make_timer_bot(i, o, f))

            # bi = BotInfo()
            # bi.iq = []
            # bi.oq = [o]
            # bi.func = f
            # bi.futr = fu
            #BotManager().add_bot(bi)

            return [bi]


        elif isinstance(f, route.Route):
            # deligate with route make_bot func
            # for output
            # push not pull
            f.make_route_bot(i, o)

            # for input
            bis = []

            if len(f.start_q) != 1 or i != f.start_q[0]:

                rib= RoutInBot(i,f)
                bi=rib.make_botinfo()
                bis.append(bi)

                # fu = asyncio.ensure_future(_route_input(i, f))
                # bi_in = BotInfo()
                # bi_in.iq = [i]
                # bi_in.oq = f.get_route_input_q_desc()
                # if f.share:
                #     bi_in.oq = f.start_q + [o]
                #
                # bi_in.func = f.route_in
                # bi_in.futr = fu
                #
                # BotManager().add_bot(bi_in)
                #
                # bis.append(bi_in)

            if f.joined and (o != f.output_q):
                rob=RoutOutBot(o,f)
                bi=rob.make_botinfo()
                bis.append(bi)
                # fu = asyncio.ensure_future(_route_output(o, f))
                # bi_in = BotInfo()
                # bi_in.iq = [f.output_q]
                # bi_in.oq = [o]
                # if isinstance(f, route.Loop):
                #     bi_in.oq = [o] + f.start_q
                #
                # bi_in.func = str(f) + "route_out"
                # bi_in.futr = fu
                # BotManager().add_bot(bi_in)



            return bis



        else:
            cb=CallableBot(i,o,f)
            bi=cb.make_botinfo()
            return [bi]
            # fu = asyncio.ensure_future(_make_bot(i, o, f))
            # bi = BotInfo()
            # bi.iq = [i]
            # bi.oq = [o]
            # bi.func = f
            # bi.futr = fu
            #
            # BotManager().add_bot(bi)
            # return [bi]


class BotFlow(object):

    @classmethod
    def stop(cls):
        exit(-1)

    @classmethod
    def run(cls):
        BotFrame.run()

    @classmethod
    def render(cls, filename):
        BotFrame.render(filename)

    @classmethod
    def debug_print(cls):
        BotManager().debug_print()
        QueueManager().debug_print()
        #Databoard().debug_print()


    @classmethod

    def enable_debug(cls):
        config.debug=True