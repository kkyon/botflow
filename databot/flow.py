import asyncio
import logging
from databot.botframe import BotFrame,call_wrap,raw_value_wrap
import collections
from databot.config import config
import  databot.queue  as queue
import typing
from databot.bdata import Bdata,BotControl,Retire

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


def ensure_list(v):
    '''make sure all ways return a list'''
    #? None >> [] ?
    if not isinstance(v,list):
        return [v]
    else:
        return v
class Route(object):

    def __init__(self, *args, route_type=object,route_func=None, share=True, join=False):

        self.in_table = RouteTable()
        self.out_table = RouteTable()
        self.args = args
        self.route_type=ensure_list(route_type)

        self.share = share
        self.joined = join
        self.start_q=None
        self.output_q=None
        self.route_func=route_func
        if self.route_func is not None and not isinstance(self.route_func,typing.Callable):
            raise Exception('route_func not callable')



        if hasattr(self, 'route_type') and not isinstance(self.route_type, list):
            self.route_type = [self.route_type]


    def get_route_input_q_desc(self):
        qs=[]
        qs.extend(self.start_q)
        if self.share:
            qs.append(self.output_q)

        return qs

    def get_route_output_q_desc(self):
        qs=[]
        if not isinstance(self.output_q,queue.NullQueue):
            qs.append(self.output_q)




        return qs
    async def _route_data(self,bdata):

        data=bdata.data
        is_signal= bdata.is_BotControl()

        matched = self.type_match(data, self.route_type) and (self.route_func is None or self.route_func(data))




        if self.share == True or is_signal:
                await self.output_q.put(bdata)
        else:
                if not matched:
                    await self.output_q.put(bdata)
                else:
                    pass


        if matched or is_signal:
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
        if  isinstance(self.output_q,queue.NullQueue):
            return
        r=await self.output_q.get()
        return r


    def make_route_bot(self,oq):
        raise NotImplementedError()


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
        q_o = queue.GodQueue()

        # get this pip own inside bot
        self.start_index = len(BotFrame.bots)
        self.q_start = q_o
        self.joined = False

        for idx,func in enumerate(args):
            q_i = q_o
            if idx == len(args)-1:
                q_o = queue.NullQueue()

            else:
                if config.replay_mode:
                    q_o=queue.CachedQueue()
                else:
                    q_o = queue.DataQueue()

            bis=BotFrame.make_bot(q_i, q_o, func)
            for b in bis:
                b.flow='main'


            if isinstance(func, Route):
                if hasattr(func, 'joined') and func.joined:
                    self.joined = True

        self.end_index = len(BotFrame.bots)
        for i in range(self.start_index, self.end_index):
            BotFrame.bots[i].pipeline = str(self)
        self.q_end = q_o

        if self.joined or config.joined_network:
            self.check_joined_node()

    @classmethod
    def get_reader_id_by_q(cls,q):
        ids=[]
        for b in BotFrame.bots:
            if cls.included(q,b.iq):
                ids.append(b.id)

        return ids

    import sys
    pickle_name = sys.modules['__main__'].__file__ + 'palyback.pk'
    @classmethod
    def  save_for_replay(cls):
        '''it will save cached data for pay back'''

        #1. get output queue of the nearest closed node in main pipe
        #2.save the data
        max_id=-1
        bot=None
        for b in BotFrame.bots:
            if b.flow=='main' and b.stoped==True:
                if b.id > max_id:
                    bot=b
                    max_id=b.id
        if bot is None:
            pass

        obj={}
        obj['botid']=max_id

        to_dump=[]
        for q in bot.oq:
            #iid=get_writor_botid(q)
            iid=[max_id]
            oid=cls.get_reader_id_by_q(q)
            to_dump.append((iid,oid,q.cache))

        obj['data'] =to_dump

        import pickle
        with open(cls.pickle_name,'wb') as f:
            pickle.dump(obj,f)

    @classmethod
    def get_q_by_bot_id_list(cls, iid, oid):
        q_of_writer=set()
        q_of_reader=set()

        for i in iid:
            for q in BotFrame.get_botinfo_by_id(i).oq:
                q_of_writer.add(q)
        for i in oid:
            for q in BotFrame.get_botinfo_by_id(i).iq:
                q_of_reader.add(q)


        r=q_of_writer&q_of_reader
        return r.pop()

    @classmethod
    def restore_for_replay(cls):
        ''''''
        #1. load data to queue
        #2. set all pre-node to closed

        import os.path
        if not os.path.isfile(cls.pickle_name):
            return

        import pickle
        with open(cls.pickle_name,'rb') as f:
            obj=pickle.load(f)

        botid=obj['botid']
        for b in BotFrame.bots:
            if b.id<=botid:
                b.stoped=True
        for data in obj['data']:
            (iid,oid,cache)=data
            q=cls.get_q_by_bot_id_list(iid, oid)
            q.load_cache(cache)

        return





    @classmethod
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


Loop=raw_value_wrap

#note drivedn by data
class Timer(Route):
    def __init__(self, delay=1, max_time=None, until=None):

        # \|/
        #  |
        #  |

        self.delay = delay
        self.max_time = max_time
        self.until = until


    def make_route_bot(self, oq):
        self.start_q=[None]
        self.output_q=oq


    async def route_in(self, data):

        await self.output_q.put(data)




class Filter(Route):

    def make_route_bot(self,oq):
        self.start_q=[oq]
        self.output_q=queue.NullQueue()


class Branch(Route):

    def is_last_one(self, list, item):
        if item == list[-1]:
            return True
        else:
            return False

    def make_route_bot(self,oq):



        q_o = queue.DataQueue()
        self.start_q=[q_o]
        self.output_q=oq
        # if self.share:
        #     self.start_q.append(oq)
        for idx,func in enumerate(self.args):
            q_i = q_o
            if  idx == len(self.args)-1:
                if self.joined :
                    q_o = self.output_q
                else:
                    q_o = queue.NullQueue()
            else:
                q_o = queue.DataQueue()



            BotFrame.make_bot(q_i, q_o, func)


class Return(Branch):


    def make_route_bot(self,oq):
        self.share=False
        self.joined=True

        super().make_route_bot(oq)



class Fork(Route):

    # |
    # | x
    # |/
    # |\
    # | x


    def make_route_bot(self,oq):
        if self.joined:
            q_o = oq
        else:
            q_o = queue.NullQueue()

        self.start_q = []
        self.output_q = oq

        #parallel in sub network not in node
        for func in self.args:
            q_i = queue.DataQueue()
            self.start_q.append(q_i)
            BotFrame.make_bot(q_i, q_o, func)


class Join(Fork):
    def make_route_bot(self,oq):
        self.share = False
        self.joined=True
        self.route_type=[object]

        super().make_route_bot(oq)




class BlockedJoin(Route):

    # |
    # | x
    # |/
    # |\
    # | x


    def make_route_bot(self,oq):

        self.start_q = []
        self.output_q=oq
        self.inner_output_q=queue.DataQueue()
        self.share = False
        self.joined=True
        self.route_type=[object]
        self.joined_result={}
        self.start_index = len(BotFrame.bots)
        for func in self.args:

            i_q = asyncio.Queue(maxsize=1)
            self.start_q.append(i_q)
            BotFrame.make_bot(i_q, self.inner_output_q, func)

        BotFrame.make_bot(self.inner_output_q,self.output_q,self.join_merge,raw_bdata=True)

        self.end_index = len(BotFrame.bots)

    async def route_in(self,bdata):
        self.joined_result[bdata.data]=[]
        bdata.ori=bdata.data
        return await super().route_in(bdata)


    async def join_merge(self,bdata):
            #await self.inner_output_q.get()
            self.joined_result[bdata.ori].append(bdata.data)
            if len(self.joined_result[bdata.ori]) == len(self.args):
                #del self.joined_result[bdata.ori]
                await self.output_q.put(Bdata(tuple(self.joined_result[bdata.ori]),ori=bdata.ori))


    def get_route_output_q_desc(self):

        return  [self.inner_output_q]















###########short name ############

F = Fork
Fi=Filter
J = Join
P = Pipe
B = Branch
T = Timer




