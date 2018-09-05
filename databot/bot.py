

import asyncio

from .base import copy_size
from .nodebase import Node
from .bdata import Bdata


from .botbase import Bot,BotManager,call_wrap,BotInfo

class CallableBot(Bot):

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
        bi.futr = self.main_loop()

        BotManager().add_bot(bi)
        self.bi=bi
        return bi


class RoutInBot(Bot):
    def __init__(self,input_q,func):
        super().__init__()
        self.input_q=input_q
        self.func=func

    def create_coro(self,data):

        coro = self.func.route_in(data)
        return coro

    def make_botinfo(self):

        bi_in = BotInfo()
        bi_in.iq = [self.input_q]
        bi_in.oq = self.func.get_route_input_q_desc()
        if self.func.share:
            bi_in.oq = self.func.start_q + [self.func.output_q]

        bi_in.func = self.func
        bi_in.futr = self.main_loop()

        BotManager().add_bot(bi_in)
        self.bi=bi_in
        return bi_in




class RoutOutBot(Bot):
    def __init__(self, input_q, func):
        super().__init__()
        self.output_q = input_q
        self.func = func


    def make_botinfo(self):

        bi_in = BotInfo()
        bi_in.iq = [self.func.output_q]
        bi_in.oq = [self.output_q]
        # if isinstance(self.func, Loop):
        #     bi_in.oq = [self.output_q] + self.func.start_q

        bi_in.func = self.func
        bi_in.futr = self.main_loop()
        BotManager().add_bot(bi_in)
        self.bi = bi_in
        return bi_in


    async def get_data_list(self):
        r=await self.func.route_out()
        return [r]

    def create_coro(self, data):

        return self.output_q.put(data)






class TimerBot(Bot):

    def __init__(self,iq,oq,timer_route):
        super().__init__(iq,oq)
        self.count=0
        self.timer_route=timer_route

    def make_botinfo(self):
        bi = BotInfo()

        bi.iq = []

        bi.oq = [self.output_q]
        bi.func = self.timer_route
        bi.futr = self.main_loop()
        self.bi = bi
        BotManager().add_bot(bi)

        return bi


    async def main_logic(self):

        self.count += 1

        if self.timer_route.max_time and self.timer_route.max_time < self.count:
                self.bi.stoped=True
                return False

        await self.output_q.put(Bdata.make_Bdata_zori(self.count))

        if self.timer_route.until is not None and self.timer_route.until():
                self.bi.stoped = True
                return False

        await asyncio.sleep(self.timer_route.delay)






