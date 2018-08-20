
import asyncio
import logging
from databot.bot import Bot,BotInfo
import collections
import queue
class RouteRule(object):
    __slots__ = ['output_q', 'type_list','share']
    def __init__(self,output_q,types_list,share):
        self.output_q=output_q
        self.type_list=types_list
        self.share=share

    def is_match(self,o):
        for t in self.type_list:
            if isinstance(o,t):
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
        self.rules=queue.PriorityQueue()

    def add_rules(self,r):
        self.rules.put(r)

    async def route(self,msg):
        matched_q=[]
        for r in self.rules.queue:
            if r.is_match(msg):
                matched_q.append(r.output_q)

                #use wait api ,it maybe blocked(wait) in a q. then block other q speed
                await  r.output_q.put(msg)
                if not r.is_share():
                    break




    pass
class Route(object):

    def __init__(self):

        self.in_table=RouteTable()
        self.out_table = RouteTable()

    def __call__(self,data):
        pass
    def make_route_bot(self, iq, oq):
        raise NotImplementedError()


    def type_match(self,msg,type_list):
        for t in type_list:
            if isinstance(msg,t):
                return True

        return False

    def q_one_to_two_type(self,input_q,main_o_q,inside_q_list,type_list=[object],share=True ):
        async def wrap():
            while True:
                item = await input_q.get()
                matched=self.type_match(item,type_list)
                is_stop=isinstance(item, StopIteration)
                if matched or is_stop:
                    for q in inside_q_list:
                        await q.put(item)

                if matched and share==False:
                    pass
                else:
                    await main_o_q.put(item)

                if is_stop:
                    await  main_o_q.put(item)
                    break

        fc = asyncio.ensure_future(wrap())

        Bot._bots.append(BotInfo(input_q, main_o_q, fc, fc))


    def q_one_to_one(self,input_q,output_q ):
        async def one_to_one(input_q,output_q):
            while True:
                item = await input_q.get()
                output_q.put_nowait(item)

                if isinstance(item, StopIteration):

                    break

        fc = asyncio.ensure_future(one_to_one(input_q,output_q))

        Bot._bots.append(BotInfo(input_q, output_q, fc, fc))



    def q_one_to_many(self,input_q ):
        async def one_to_many(input_q):
            while True:
                item = await input_q.get()
                await self.in_table.route(item)

                if isinstance(item, StopIteration):

                    break

        fc = asyncio.ensure_future(one_to_many(input_q))

        Bot._bots.append(BotInfo(input_q, None, fc, fc))

    def q_many_to_one(self,output_q,*input_q):

        for q in input_q:
            self.q_one_to_one(q,output_q)



#main pipe
class Pipe(Route):


    # |
    # |
    # |
    # |
    # |



    def __init__(self,*args):
        q_o = NullQueue()
        self.q_start = q_o
        for func in args:
            q_i = q_o
            if func == args[-1]:
                q_o = NullQueue()

            else:
                q_o = asyncio.Queue()

            Bot.make_bot(q_i, q_o, func)
        self.q_end=q_o

    def __call__(self, list):
        pass


class Join(Route):


    def make_route_bot(self,iq,oq):

        #1.
        #  |
        # / \
        # \ /
        #  |
        #2.
        #\|/
        # |
        # |

        self.q_output = oq
        self.q_in_list = []
        for func in self.args:
            q_i = asyncio.Queue()
            self.q_in_list.append(q_i)
            Bot.make_bot(q_i, self.q_output, func)


        self.q_one_to_many(iq,*self.q_in_list)






#No read inpute
class Loop(Route):
    def __init__(self,input):
        self.input=input

    def make_route_bot(self, iq, oq):


        async def nest_loop(iq,oq):

            for i in self.input:
                await oq.put(i)
            await oq.put(StopIteration())

        Bot.make_bot_raw(iq,oq,nest_loop)




class Timer(Route):
    def __init__(self, delay=1,max_time=None):



        # \|/
        #  |
        #  |

        self.delay=delay
        self.max_time=max_time



    def make_route_bot(self, iq, oq):
        async def data_route(q_i,q_o):
            count=0
            while True:
                count += 1
                if self.max_time and self.max_time < count:
                    break

                await asyncio.sleep(self.delay)

                q_o.put_nowait('ping %s' %(count))


            await q_o.put(StopIteration())


        Bot.make_bot_raw(iq,oq,data_route)




    async def __call__(self, data):
        pass






class Branch(Route):


    # |
    # |
    # |- - -x
    # |
    def __init__(self,*args,route_type=object,share=True):
        self.args=args
        if isinstance(route_type,list):
            self.route_type=route_type
        else:
            self.route_type = [route_type]
        self.share=share
        super().__init__()

    def is_last_one(self,list,item):
        if item == list[-1]:
            return True
        else:
            return False
    def make_route_bot(self, iq, oq):


        self.q_start = asyncio.Queue()
        q_o=self.q_start
        for func in self.args:
            q_i = q_o
            if self.is_last_one(self.args,func):
                q_o= NullQueue()
            else:
                q_o = asyncio.Queue()

            Bot.make_bot(q_i, q_o, func)
        # self.in_table.add_rules(RouteRule(oq, [object], True))
        # self.in_table.add_rules(RouteRule(self.q_start, [self.route_type], self.share))
        self.q_one_to_two_type(iq,oq,[self.q_start],self.route_type,self.share)




    def __call__(self, data):
        logging.debug('branch'+str(type(data)))
        self.q_start.put_nowait(data)
        return data



#无法知道该类是被那里使用。更复杂实现是需要控制所有route初始化的顺序，需要外层初始化结束，建in,out队列传递到内侧
#make bot时候，对route只需要建立队列关系，而不需要，使用for循环来处理call
class Passby(Route):

    # |
    # | x
    # |/
    # |\
    # | x
    def __init__(self,*args,route_type=object,share=True):
        self.args=args
        if isinstance(route_type,list):
            self.route_type=route_type
        else:
            self.route_type = [route_type]
        self.share=share
        super().__init__()

    def make_route_bot(self, iq, oq):
        q_o = NullQueue()
        self.q_in_list = []
        for func in self.args:
            q_i = asyncio.Queue()
            self.q_in_list.append(q_i)
            Bot.make_bot(q_i, q_o, func)


        self.q_one_to_two_type(iq,oq,self.q_in_list,self.route_type,self.share)






class ListQueue(asyncio.Queue):
    def __init__(self,it):
        self.it=it
        super().__init__()


    def _init(self, maxsize):
        self._queue = collections.deque(self.it)
class NullQueue(asyncio.Queue):

    # |
    # X
    def __init__(self):
        pass
    def empty(self):
        return False
    def put_nowait(self, item):
        raise NotImplementedError()

    async def put(self, item):
        #do nothing
        await asyncio.sleep(0)

    async def get(self):
        await asyncio.sleep(0,)

    def get_nowait(self):
        raise NotImplementedError()







