import asyncio
import logging
from .nodebase import Node
from .bdata import Bdata
from .config import config
import typing,types
from .botbase import BotBase,BotManager,BotInfo,filter_out
from .base import BotExit,flatten

logger = logging.getLogger(__name__)

class CallableBot(BotBase):

    def __init__(self,input_q,output_q,func):
        super().__init__()
        self.input_q=input_q
        self.output_q=output_q
        self.func=func
        self.raw_bdata=False
        self.type_hint=None

        if isinstance(self.func,types.FunctionType):
            d=typing.get_type_hints(self.func)
        else:
            d=typing.get_type_hints(self.func.__call__)
        if len(d) == 1:
            for k,v in d.items():
                self.type_hint=v
        elif len(d) >1:
            raise Exception("{} more one param")



    async def pre_hook(self):

        if isinstance(self.func, Node):
            await self.func.node_init()

            self.raw_bdata = self.func.raw_bdata

        else:
            self.raw_bdata = False

    async def post_hook(self):
        if isinstance(self.func, Node):
            await self.func.node_close()

    async def sync_to_async(self, f, data):
        r=f(data)
        if isinstance(r,types.CoroutineType):
            r=await r
        return r

    async def call_wrap_r(self,func, bdata):
        self.consumed_count += 1
        logger.debug('call_wrap' + str(type(func)) + str(func))

        if bdata.data is None:
            return None
        result = None

        if not isinstance(bdata, Bdata):
            raise Exception('bad data {}'.format(bdata))

        try:

            if isinstance(func, Node) and func.raw_bdata:
                param = bdata
            else:
                param = bdata.data

            if hasattr(func, 'boost_type'):
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, func, param)


            else:
                r_or_c = func(param)
                if isinstance(r_or_c, types.CoroutineType):
                    r_or_c = await r_or_c

                if filter_out(r_or_c):
                    result = None
                else:
                    result = r_or_c
        except Exception as e:

            if config.exception_policy == config.Exception_raise:
                raise e
            elif config.exception_policy == config.Exception_ignore:
                result = None
            elif config.exception_policy == config.Exception_pipein:
                result = e
            elif config.exception_policy == config.Exception_retry:
                raise e  # TODO
            else:
                raise Exception('undefined exception policy')

        return result

    async def merge_list(self,func,bdata):
        tasks=[]
        for d in  flatten(bdata.data): #TODO to deal with too large list and generator!!!
            if self.type_hint is None or isinstance(d,self.type_hint):
                task=asyncio.ensure_future(self.call_wrap_r(func, Bdata(d,bdata.ori)))
                tasks.append(task)

        #will keep order
        r=await asyncio.gather(*tasks)

        return r

    async def append_q(self,call_wrap_r,func,bdata,q):
        r=await call_wrap_r(func,bdata)
        logger.debug("exe {} get data {}".format(func,r))
        all_none = False
        if isinstance(r,list):
            all_none = True
            for i in r:
                if not i is None:
                    all_none=False
            if all_none == False:
                self.produced_count += 1
                await q.put(Bdata(r, bdata.ori))

        elif isinstance(r,typing.Generator):
            for i in r:
                self.produced_count+=1
                await q.put(Bdata(i, bdata.ori))

        else:
            if r is not None :
                self.produced_count += 1
                await q.put(Bdata(r,bdata.ori))



    def create_coro(self,bdata):

        if isinstance(bdata.data,(list,types.GeneratorType)) \
                and not(self.raw_bdata)\
                and ( self.type_hint is not list):
               #and not isinstance(self.func,Node):


            if self.type_hint is not None:
                if isinstance(bdata.data, self.type_hint): #the func request a list
                    coro = self.append_q(self.merge_list,self.func, bdata, self.output_q)
                else:
                    coro = self.output_q.put(bdata)

            else:
                coro = self.append_q(self.merge_list,self.func, bdata, self.output_q)

            return coro


        else:
            if self.type_hint is not None :
                if isinstance(bdata.data,self.type_hint):
                    coro = self.append_q(self.call_wrap_r,self.func, bdata, self.output_q)
                else:
                    coro = self.output_q.put(bdata)

            else:
                coro = self.append_q(self.call_wrap_r,self.func, bdata, self.output_q)

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

        config.check_stoping = False



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
            config.check_stoping=True
            raise BotExit()



        self.count += 1



        await self.output_q.put(Bdata.make_Bdata_zori(self.count))



        await asyncio.sleep(self.timer_route.delay)





class LoopBot(BotBase):
    def __init__(self, input_q, output_q, it):

        super().__init__()
        self.input_q=input_q
        self.output_q = output_q
        self.it = it
        config.check_stoping=False

    def make_botinfo(self):


        bi = BotInfo()

        bi.iq = [self.input_q]

        bi.oq = [self.output_q]
        bi.func = self
        bi.main_coro = self.main_loop()
        self.bi = bi
        BotManager().add_bot(bi)

        return bi
    async def get_data_list(self):
        r=await self.input_q.get()
        return r

    async def main_logic(self):
        data_list = await self.get_data_list()
        config.check_stoping = False
        for v in self.it:
            await self.output_q.put(Bdata.make_Bdata_zori(v))

        config.check_stoping = True



