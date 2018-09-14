import botflow.queue  as queue
import typing
from .bdata import Databoard
from .base import get_loop

class RouteRule(object):
    __slots__ = ['output_q', 'type_list', 'share']

    def __init__(self, output_q, types_list, share):
        self.output_q = output_q
        self.type_list = types_list
        self.share = share
        self.loop=get_loop()

    def is_match(self, o):
        for t in self.type_list:
            if isinstance(o, t):
                return True

        return False

    def is_share(self):
        return self.share

    def __eq__(self, other):
        return False

    def __lt__(self, other):

        if self.share == False:
            return True
        else:
            return False


class RouteTable(object):
    __slots__ = ['rules']

    def __init__(self):
        self.rules = queue.DataQueue()

    def add_rules(self, r):
        self.rules.put(r)

    async def route(self, msg):
        matched_q = []
        for r in self.rules.queue:
            if r.is_match(msg):
                matched_q.append(r.output_q)

                # use wait api ,it maybe blocked(wait) in a q. then block other q speed
                await  r.output_q.put(msg)
                if not r.is_share():
                    break

    pass


def ensure_list(v):
    '''make sure all ways return a list'''
    #? None >> [] ?
    if not isinstance(v,list):
        return [v]
    else:
        return v
class Route(object):

    def __init__(self, *args, route_type=object,route_func=None, share=True, join=False):

        self.name=str(self.__class__)
        self.in_table = RouteTable()
        self.out_table = RouteTable()
        self.args = args
        self.route_type=ensure_list(route_type)
        self.databoard = Databoard()
        self.share = share
        self.joined = join
        self.outer_iq=None
        self.outer_oq=None
        self.loop=get_loop()
        self.start_q=None
        self.output_q=None
        self.route_func=route_func
        if self.route_func is not None and not isinstance(self.route_func,typing.Callable):
            raise Exception('route_func not callable')



        if hasattr(self, 'route_type') and not isinstance(self.route_type, list):
            self.route_type = [self.route_type]


    def routeout_out_q(self):
        return [self.outer_oq]

    def routeout_in_q(self):
        qs=[]
        if isinstance(self.output_q,list):
            for q in self.output_q:
                if isinstance(self.output_q, queue.SinkQueue):
                    continue
                qs.append(q)

        elif not isinstance(self.output_q, queue.SinkQueue):
            qs.append(self.output_q)

        return qs

    def routein_out_q(self):
        if self.share and not isinstance(self.outer_oq, queue.SinkQueue):
            return self.start_q+[self.outer_oq]
        else:
            return self.start_q

    def routein_in_q(self):
        return [self.outer_iq]



    async def _route_data(self,bdata):

        data=bdata.data
        # is_signal= bdata.is_BotControl()

        matched = self.type_match(data, self.route_type) and (self.route_func is None or self.route_func(data))




        if self.share == True:
                bdata.incr()
                await self.outer_oq.put(bdata)
        else:
                if not matched:
                    bdata.incr()
                    await self.outer_oq.put(bdata)
                else:
                    pass


        if matched:
            bdata.incr(n=len(self.start_q))
            for q in self.start_q:
                await q.put(bdata)


    async def __call__(self, data):

        if isinstance(data,list):
            for d in data:
                await self._route_data(data)
        else:
            await self._route_data(data)

        return

    async def route_in(self,data):
        if isinstance(data,list):
            for d in data:
                await self._route_data(data)
        else:
            await self._route_data(data)

        return

    async def route_out(self):

        # for q in self.output_q:
        if  isinstance(self.output_q, queue.SinkQueue):
            return
        r=await self.output_q.get()
        return r


    def make_route_bot(self,iq,oq):
        '''the out side input and outpt queue'''
        raise NotImplementedError()


    @classmethod
    def type_match(cls, msg, type_list):
        for t in type_list:
            if isinstance(msg, t):
                return True

        return False


