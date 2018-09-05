import asyncio
from . import route
import botflow.nodebase as node
import typing
import types
from .config import config
import logging
from botflow.bdata import Bdata
from .botbase import BotManager, BotInfo,raw_value_wrap
from .bot import CallableBot,RouteOutBot,RouteInBot,TimerBot
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
    def make_bot(cls, i, o, f):



        if not isinstance(f, typing.Callable):
            f = raw_value_wrap(f)

        if isinstance(f, route.Timer):
            f.make_route_bot(i,o)

            tb=TimerBot(i,o,f)
            bi=tb.make_botinfo()

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

            if not cmp_q_list(f.routein_in_q(),f.routein_out_q()):

                rib= RouteInBot(i,f)
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

            if f.joined and not cmp_q_list(f.routeout_in_q(),f.routeout_out_q()):
                rob=RouteOutBot(o,f)
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
