import asyncio
import logging
from databot.botframe import BotFrame
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

    def __init__(self):

        self.in_table = RouteTable()
        self.out_table = RouteTable()

        if hasattr(self, 'route_type') and not isinstance(self.route_type, list):
            self.route_type = [self.route_type]

    def __call__(self, data):
        pass

    def make_route_bot(self, iq, oq):
        raise NotImplementedError()

    def create_queue(self) -> asyncio.Queue:
        return asyncio.Queue(maxsize=128)

    @classmethod
    def type_match(cls, msg, type_list):
        for t in type_list:
            if isinstance(msg, t):
                return True

        return False

    #
    #
    # def q_one_to_one(self,input_q,output_q ):
    #     async def one_to_one(input_q,output_q):
    #         while True:
    #             item = await input_q.get()
    #             output_q.put_nowait(item)
    #
    #             if isinstance(item, Retire):
    #
    #                 break
    #
    #     BotFrame.make_bot_raw(input_q, output_q, one_to_one(input_q,output_q))
    #
    #
    #
    #
    #
    #
    # def q_one_to_many(self,input_q ):
    #     async def one_to_many(input_q):
    #         while True:
    #             item = await input_q.get()
    #             await self.in_table.route(item)
    #
    #             if isinstance(item, Retire):
    #
    #                 break
    #
    #     BotFrame.make_bot_raw(input_q, None, one_to_many(input_q))
    #
    #
    # def q_many_to_one(self,output_q,*input_q):
    #
    #     for q in input_q:
    #         self.q_one_to_one(q,output_q)


# main pipe
class Pipe(Route):

    # |
    # |
    # |
    # |

    def __init__(self, *args):
        q_o = NullQueue()

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

    def check_joined_node(self):
        for i in range(self.start_index, self.end_index):
            bot = BotFrame.bots[i]
            count = 0
            for j in range(self.start_index, self.end_index):

                for q in BotFrame.bots[j].oq:
                    if bot.iq is q:
                        count += 1
                        bot.parents.append(BotFrame.bots[j])

            bot.parent_count = count

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
    def __init__(self, input):
        self.input = input
        self.joined = False

    def make_route_bot(self, iq, oq):
        async def nest_loop(oq):
            bi = BotFrame.get_botinfo()
            for i in self.input:
                await oq.put(i)

            bi.stoped = True
            BotFrame.ready_to_stop(bi)

        BotFrame.make_bot_raw(None, oq, nest_loop(oq))


class Timer(Route):
    def __init__(self, delay=1, max_time=None, until=None):

        # \|/
        #  |
        #  |

        self.delay = delay
        self.max_time = max_time
        self.until = until

    def make_route_bot(self, iq, oq):
        async def data_route(q_o):
            count = 0
            bi = BotFrame.get_botinfo()
            while True:
                count += 1

                if self.max_time and self.max_time < count:
                    break

                q_o.put_nowait(count)

                if self.until is not None and self.until():
                    break
                await asyncio.sleep(self.delay)

            bi.stoped = True
            BotFrame.ready_to_stop(bi)

            # await q_o.put(Retire())

        BotFrame.make_bot_raw(None, oq, data_route(oq))

    async def __call__(self, data):
        pass


class Branch(Route):

    # |
    # |
    # |- - -x
    # |
    def __init__(self, *args, route_type=object, share=True, join=False):
        self.args = args
        if isinstance(route_type, list):
            self.route_type = route_type
        else:
            self.route_type = [route_type]
        self.share = share
        self.joined = join
        super().__init__()

    def is_last_one(self, list, item):
        if item == list[-1]:
            return True
        else:
            return False

    def make_route_bot(self, iq, oq):

        self.q_start = self.create_queue()
        q_o = self.q_start
        BotFrame.q_one_to_two_type(iq, oq, [self.q_start], self.route_type, self.share)
        for func in self.args:
            q_i = q_o
            if self.is_last_one(self.args, func):
                if self.joined:
                    q_o = oq
                else:
                    q_o = NullQueue()
            else:
                q_o = self.create_queue()

            BotFrame.make_bot(q_i, q_o, func)

    def __call__(self, data):
        logging.debug('branch' + str(type(data)))
        self.q_start.put_nowait(data)
        return data


# 无法知道该类是被那里使用。更复杂实现是需要控制所有route初始化的顺序，需要外层初始化结束，建in,out队列传递到内侧
# make bot时候，对route只需要建立队列关系，而不需要，使用for循环来处理call
class Fork(Route):

    # |
    # | x
    # |/
    # |\
    # | x
    def __init__(self, *args, route_type=object, share=True, join=False):
        self.args = args
        if isinstance(route_type, list):
            self.route_type = route_type
        else:
            self.route_type = [route_type]
        self.share = share
        self.joined = join
        super().__init__()

    def make_route_bot(self, iq, oq):
        if self.joined:
            q_o = oq
        else:
            q_o = NullQueue()
        self.q_in_list = []
        for func in self.args:
            q_i = asyncio.Queue()
            self.q_in_list.append(q_i)
            BotFrame.make_bot(q_i, q_o, func)

        BotFrame.q_one_to_two_type(iq, oq, self.q_in_list, self.route_type, self.share)


class Join(Fork):
    def __init__(self, *args, route_type=object, share=True, join=False):
        super().__init__(args, route_type, share, join=True)


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
