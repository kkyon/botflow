import asyncio
from . import route
import botflow.nodebase as node
import typing
import types
from .config import config
import logging
from botflow.bdata import Bdata
from .botbase import BotManager, BotInfo,raw_value_wrap
from .bot import CallableBot,RouteOutBot,RouteInBot,TimerBot,LoopBot
from .queue import NullQueue,QueueManager
logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)s:%(message)s', level=logging.INFO)
from .base import BotExit




def cmp_q_list(aql,bql):
    a=set()
    b=set()

    for aq in aql:
        if not isinstance(aq,NullQueue):
            a.add(aq)

    for bq in bql:
        if not isinstance(bq, NullQueue):
            b.add(bq)

    if len(a) !=len(b):
        return False

    if a == b:
        return True

    return False


from concurrent import futures
executor = futures.ThreadPoolExecutor(max_workers=10)
asyncio.get_event_loop().set_default_executor(executor)

class BotFrame(object):



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
    def make_bot_raw(cls, iq, oq, func,coro):
        task = asyncio.ensure_future(coro)
        bi = BotInfo()
        bi.iq = iq
        if not isinstance(oq, list):
            oq = [oq]
        bi.oq = oq
        bi.main_coro = coro
        bi.main_task= task
        bi.func = func

        BotManager().add_bot(bi)

    @classmethod
    def make_bot(cls, i, o, f):



        if not isinstance(f, typing.Callable):
            f = raw_value_wrap(f)
            # if isinstance(f,(list,types.GeneratorType,range)):
            #
            #     tb = LoopBot(i, o, f)
            #     bi = tb.make_botinfo()
            #     return [bi]
            #
            #
            #
            # else:
            #     f = raw_value_wrap(f)

        if isinstance(f, route.Timer):
            f.make_route_bot(i,o)

            tb=TimerBot(i,o,f)
            bi=tb.make_botinfo()



            return [bi]


        elif isinstance(f, route.Route):

            f.make_route_bot(i, o)


            bis = []

            if not cmp_q_list(f.routein_in_q(),f.routein_out_q()):

                rib= RouteInBot(i,f)
                bi=rib.make_botinfo()
                bis.append(bi)



            if f.joined and not cmp_q_list(f.routeout_in_q(),f.routeout_out_q()):
                rob=RouteOutBot(o,f)
                bi=rob.make_botinfo()
                bis.append(bi)




            return bis



        else:
            cb=CallableBot(i,o,f)
            bi=cb.make_botinfo()
            return [bi]

