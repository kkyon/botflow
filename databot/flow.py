import asyncio
import logging
from databot.botframe import BotFrame,call_wrap,BotControl
import collections
from databot.config import config
import queue


class RouteRule(object):
    __slots__ = ['output_q', 'type_list', 'share']

    def __init__(self, output_q, types_list, share):
        self.output_q = output_q
        self.type_list = types_list
        self.share = share

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
        self.rules = queue.PriorityQueue()

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


class Route(object):

    def __init__(self, *args, route_type=object, share=True, join=False):

        self.in_table = RouteTable()
        self.out_table = RouteTable()
        self.args = args
        if isinstance(route_type, list):
            self.route_type = route_type
        else:
            self.route_type = [route_type]

        self.share = share
        self.joined = join
        self.start_q=None
        self.output_q=None


        if hasattr(self, 'route_type') and not isinstance(self.route_type, list):
            self.route_type = [self.route_type]

    async def start_q_put(self,data):


        is_signal= isinstance(data,BotControl)

        matched = self.type_match(data, self.route_type)


        if self.share == True or is_signal:
                await self.output_q.put(data)
        else:
                if not matched:
                    await self.output_q.put(data)
                else:
                    pass


        if matched or is_signal:
            for q in self.start_q:
                await q.put(data)
            # if isinstance(self.start_q,list):
            #     for q in self.start_q:
            #         await q.put(data)
            # else:
            #     await self.start_q.put(data)

    async def __call__(self, data):

        if isinstance(data,list):
            for d in data:
                await self.start_q_put(data)
        else:
            await self.start_q_put(data)

        return



    def make_route_bot(self, iq, oq):
        raise NotImplementedError()

    def create_queue(self) -> asyncio.Queue:
        q=asyncio.Queue(maxsize=128)

        return q

    @classmethod
    def type_match(cls, msg, type_list):
        for t in type_list:
            if isinstance(msg, t):
                return True

        return False




# main pipe
class Pipe(Route):

    # |
    # |
    # |
    # |

    def __init__(self, *args):
        q_o = GodQueue()

        # get this pip own inside bot
        self.start_index = len(BotFrame.bots)
        self.q_start = q_o
        self.joined = False
        for func in args:
            q_i = q_o
            if func == args[-1]:
                q_o = NullQueue()

            else:
                q_o = self.create_queue()

            BotFrame.make_bot(q_i, q_o, func)
            if isinstance(func, Route):
                if hasattr(func, 'joined') and func.joined:
                    self.joined = True

        self.end_index = len(BotFrame.bots)
        for i in range(self.start_index, self.end_index):
            BotFrame.bots[i].pipeline = str(self)
        self.q_end = q_o

        if self.joined or config.joined_network:
            self.check_joined_node()


    def included(self,iq,oq):
        if not isinstance(iq,list):
            iq=[iq]
        if not isinstance(oq,list):
            oq=[oq]

        for q in iq:
            for _oq in oq:
                if q is _oq:
                    return True
        return False
    def check_joined_node(self):
        for i in range(self.start_index, self.end_index):
            bot = BotFrame.bots[i]
            count = 0
            for j in range(self.start_index, self.end_index):

                for q in BotFrame.bots[j].oq:
                    if self.included(bot.iq, q):
                    #if bot.iq is q:
                        count += 1
                        bot.parents.append(BotFrame.bots[j])



    def finished(self):
        for i in range(self.start_index, self.end_index):
            fu = BotFrame.bots[i].futr
            if not fu.done() and not fu.cancelled():
                return False
        return True

    def __call__(self, list):
        pass

    def __repr__(self):
        return 'Pip_' + str(id(self))


# No read inpute
class Loop(Route):



    def make_route_bot(self, iq, oq):
        self.input = self.args[0]
        self.joined = True
        self.share=False
        self.start_q=[iq]
        self.output_q =oq


    async def __call__(self, data):
        if isinstance(data,BotControl):
            await self.output_q.put(data)
            return
        for i in self.input:
            await self.output_q.put(i)




#note drivedn by data
class Timer(Route):
    def __init__(self, delay=1, max_time=None, until=None):

        # \|/
        #  |
        #  |

        self.delay = delay
        self.max_time = max_time
        self.until = until

    def make_route_bot(self, iq, oq):
        self.start_q=[None]
        self.output_q=oq


    async def __call__(self, data):

        await self.output_q.put(data)





def raw_value_wrap(raw_value):

    def _raw_value_wrap(data):
        return raw_value

    return _raw_value_wrap


class Branch(Route):

    def is_last_one(self, list, item):
        if item == list[-1]:
            return True
        else:
            return False

    def make_route_bot(self, iq, oq):


        self.output_q = oq
        q_o = self.create_queue()
        self.start_q=[q_o]
        for func in self.args:
            q_i = q_o
            if self.is_last_one(self.args, func):
                if self.joined:
                    q_o = oq
                else:
                    q_o = NullQueue()
            else:
                q_o = self.create_queue()

            if isinstance(func,(str,bytes,int,float))  :
                func=raw_value_wrap(func)

            BotFrame.make_bot(q_i, q_o, func)



class Return(Branch):


    def make_route_bot(self, iq, oq):
        self.share=False
        self.joined=True

        super().make_route_bot(iq,oq)


# 无法知道该类是被那里使用。更复杂实现是需要控制所有route初始化的顺序，需要外层初始化结束，建in,out队列传递到内侧
# make bot时候，对route只需要建立队列关系，而不需要，使用for循环来处理call
class Fork(Route):

    # |
    # | x
    # |/
    # |\
    # | x


    def make_route_bot(self, iq, oq):
        if self.joined:
            q_o = oq
        else:
            q_o = NullQueue()

        self.start_q = []
        self.output_q = oq

        #parallel in sub network not in node
        for func in self.args:
            q_i = asyncio.Queue()
            self.start_q.append(q_i)
            BotFrame.make_bot(q_i, q_o, func)


class Join(Fork):
    def make_route_bot(self, iq, oq):
        self.share = False
        self.joined=True
        self.route_type=[object]

        super().make_route_bot(iq,oq)




#方案1，放入一个等待结构，超时后需要将任务杀死
#方案2 随机处理，在出口处，汇总合并数据，
class BlockedJoin(Route):

    # |
    # | x
    # |/
    # |\
    # | x


    def make_route_bot(self, iq,oq):

        self.start_q = []
        self.tmp_output_q=[]
        self.output_q=oq
        self.share = False
        self.joined=True
        self.route_type=[object]

        self.start_index = len(BotFrame.bots)
        for func in self.args:

            i_q = asyncio.Queue(maxsize=1)
            o_q = self.create_queue()
            self.start_q.append(i_q)
            self.tmp_output_q.append(o_q)
            BotFrame.make_bot(i_q, o_q, func)

        self.end_index = len(BotFrame.bots)


    def check(self):
        for i in range(self.start_index, self.end_index):
            bot = BotFrame.bots[i]
            if not bot.idle:
                return False
        for q in self.start_q:
            if not q.empty():
                return False
        return True

    async def compeleted(self):
        while True:
            s=self.check()

            if s:
                return True
            await asyncio.sleep(2)


    async def put_batch_q(self,data,qlist):

        tasks=[]
        for q in qlist:
            task=q.put(data)
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def gut_batch_q(self, qlist):

        tasks = []
        for q in qlist:
            #TODO need get all extension
            task = q.get()
            tasks.append(task)

        r=await asyncio.gather(*tasks)
        return tuple(r)



    async def __call__(self, data):


            await self.put_batch_q(data,self.start_q)
            r=await self.gut_batch_q(self.tmp_output_q)
            await self.output_q.put(r)
            # await self.compeleted()
            # for q in  self.start_q:
            #     await q.put(data)
            #
            # await self.compeleted()
            # result=[]
            # for q in self.tmp_output_q:
            #     if q.empty():
            #         continue
            #     if q.qsize()==1:
            #         i=await q.get()
            #         result.append(i)
            #
            #     else:
            #         one_result=[]
            #         while q.empty():
            #             i=await q.get()
            #             one_result.append(i)
            #         result.append(tuple(one_result))
            #
            # await self.output_q.put(tuple(result))






        #unable to paralle in network
        # async def joined_network(data):
        #     tasks=[]
        # #parallel in sub network not in node
        #     o_q = self.create_queue()
        #     in_q_list=[]
        #     for func in self.args:
        #         i_q = self.create_queue()
        #         in_q_list.append(i_q)
        #         # BotFrame.make_bot(i_q, o_q, func)
        #         task=asyncio.ensure_future(call_wrap(func, data, data, o_q))
        #         tasks.append(task)
        #
        #     for q in in_q_list:
        #         await q.put(data)
        #     await asyncio.gather(*tasks)
        #
        #     results=[]
        #     while not o_q.empty():
        #         results.append(o_q.get_nowait())
        #
        #
        #     return tuple(results)



        #bi=BotFrame.make_bot(self.start_q, oq, joined_network)









###########short name ############

F = Fork
J = Join
P = Pipe
B = Branch
T = Timer
L = Loop


class ListQueue(asyncio.Queue):
    def __init__(self, it):
        self.it = it
        super().__init__()

    def _init(self, maxsize):
        self._queue = collections.deque(self.it)


class GodQueue(asyncio.Queue):

    # |
    # X
    def __init__(self):
        self.last_put = None
        self._data=[0]
        pass

    def qsize(self):
        return len(self._data)
    def empty(self):
        return len(self._data)==0

    def put_nowait(self, item):
        raise NotImplementedError()

    async def put(self, item):
        raise NotImplementedError()

    async def get(self):
        return self.get_nowait()


    def get_nowait(self):
        d=self._data[0]
        self._data=[]
        return d


class NullQueue(asyncio.Queue):

    # |
    # X
    def __init__(self):
        self.last_put = None
        pass

    def empty(self):
        return False

    def put_nowait(self, item):
        raise NotImplementedError()

    async def put(self, item):
        # do nothing
        self.last_put = item
        await asyncio.sleep(0)

    async def get(self):
        await asyncio.sleep(0, )

    def get_nowait(self):
        raise NotImplementedError()


