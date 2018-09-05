

import asyncio

from .base import copy_size
from .nodebase import Node
from .bdata import Bdata
from .config import config

from .botbase import BotBase,BotManager,call_wrap,BotInfo

class CallableBot(BotBase):

    def __init__(self,input_q,output_q,func):
        super().__init__()
        self.input_q=input_q
        self.output_q=output_q
        self.func=func
        self.raw_bdata=False


    async def pre_hook(self):

        if isinstance(self.func, Node):
            await self.func.node_init()

            self.raw_bdata = self.func.raw_bdata

        else:
            self.raw_bdata = False

    async def post_hook(self):
        if isinstance(self.func, Node):
            await self.func.node_close()


    def create_coro(self,data):

        coro = call_wrap(self.func, data, self.input_q, self.output_q, raw_bdata=self.raw_bdata)
        return coro

    def make_botinfo(self):


        bi = BotInfo()
        bi.iq = [self.input_q]
        bi.oq = [self.output_q]
        bi.func = self.func
        bi.main_coro = self.main_loop()

        BotManager().add_bot(bi)
        self.bi=bi
        return bi

class RouteMixin(object):
        pass

class RouteInBot(BotBase):
    def __init__(self,input_q,func):
        super().__init__()
        self.input_q=input_q
        self.func=func

    def create_coro(self,data):

        coro = self.func.route_in(data)
        return coro

    def make_botinfo(self):

        bi = BotInfo()
        bi.iq = self.func.routein_in_q()
        bi.oq = self.func.routein_out_q()
        bi.func = self.func
        bi.main_coro = self.main_loop()

        BotManager().add_bot(bi)
        self.bi=bi
        return bi




class RouteOutBot(BotBase):
    def __init__(self, input_q, func):
        super().__init__()
        self.output_q = input_q
        self.func = func


    def make_botinfo(self):

        bi = BotInfo()
        bi.iq = self.func.routeout_in_q()
        bi.oq = self.func.routeout_out_q()
        bi.func = self.func
        bi.main_coro = self.main_loop()

        BotManager().add_bot(bi)
        self.bi=bi
        return bi


    async def get_data_list(self):
        r=await self.func.route_out()
        return [r]

    def create_coro(self, data):

        return self.output_q.put(data)






class TimerBot(BotBase):

    def __init__(self,iq,oq,timer_route):
        super().__init__()
        self.count=0
        self.timer_route=timer_route
        self.output_q=oq
        self.input_q=None




    def make_botinfo(self):


        bi = BotInfo()

        bi.iq = []

        bi.oq = [self.output_q]
        bi.func = self.timer_route
        bi.main_coro = self.main_loop()
        self.bi = bi
        BotManager().add_bot(bi)

        return bi

    def check_stop(self):

        if self.timer_route.max_time and self.timer_route.max_time < self.count:
                self.bi.stoped=True
                return True
        # if self.timer_route.until is not None and self.timer_route.until():
        #         self.bi.stoped = True
        #         return True
        return False


    async def main_logic(self):

        if self.check_stop():
            config.main_lock.release()
            await asyncio.sleep(10000)

        self.count += 1



        await self.output_q.put(Bdata.make_Bdata_zori(self.count))



        await asyncio.sleep(self.timer_route.delay)






