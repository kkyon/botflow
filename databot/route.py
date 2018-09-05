import asyncio
import logging
from .botframe import BotFrame
from .config import config
import  databot.queue  as queue
from databot.bdata import Bdata,Databoard
from .botbase import BotManager
from .routebase import Route

# main pipe
class Pipe(Route):

    # |
    # |
    # |
    # |

    def __init__(self, *args):
        self.bm=BotManager()
        q_o = queue.DataQueue()

        # get this pip own inside bot
        self.start_index = len(self.bm.get_bots())
        self.q_start = q_o
        self.joined = False
        import sys
        self.pickle_name = sys.modules['__main__'].__file__ + 'palyback.pk'
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


            # if isinstance(func, Route):
            #     if hasattr(func, 'joined') and func.joined:
            #         self.joined = True

        self.end_index = len(self.bm.get_bots())

        bots=self.bm.get_bots()

        self.all_q = set()
        for i in range(self.start_index, self.end_index):
                bot=bots[i]
                bot.pipeline = self
                for q in bot.iq:
                    self.all_q.add(q)
                for q in bot.oq:
                    self.all_q.add(q)


        self.q_end = q_o



        self.bm.make_bot_flowgraph(self)
        # if self.joined or config.joined_network:
        #     self.check_joined_node()

        #start to work
        self.q_start.put_nowait(Bdata.make_Bdata_zori(0))






    @classmethod
    def empty(cls):
        bm=BotManager()
        bi=bm.get_botinfo_current_task()
        for q in bi.pipeline.all_q:
            if isinstance(q,queue.NullQueue):
                continue
            if q.empty() == False:
                print("id:{}".format(id(q)))
                return False


        for bot in bm.get_bots_bypipe(bi.pipeline):
            fu = bot.futr
            if bi == bot:
                continue
            if bot.idle ==False and not(bot.stoped):
                print(bot.func)
                return False




        return True

    def  save_for_replay(self):
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
            oid=self.bm.get_reader_id_by_q(q)
            to_dump.append((iid,oid,q.cache))

        obj['data'] =to_dump

        import pickle
        with open(self.pickle_name,'wb') as f:
            pickle.dump(obj,f)


    def get_q_by_bot_id_list(self, iid, oid):
        q_of_writer=set()
        q_of_reader=set()

        for i in iid:
            for q in self.bm.get_botinfo_by_id(i).oq:
                q_of_writer.add(q)
        for i in oid:
            for q in self.bm.get_botinfo_by_id(i).iq:
                q_of_reader.add(q)


        r=q_of_writer&q_of_reader
        return r.pop()


    def restore_for_replay(self):
        ''''''

        import os.path
        if not os.path.isfile(self.pickle_name):
            return

        import pickle
        with open(self.pickle_name,'rb') as f:
            obj=pickle.load(f)

        botid=obj['botid']
        for b in BotFrame.bots:
            if b.id<=botid:
                b.stoped=True
        for data in obj['data']:
            (iid,oid,cache)=data
            q=self.get_q_by_bot_id_list(iid, oid)
            q.load_cache(cache)

        return











    def finished(self):
        bm=BotManager()
        for bot in bm.get_bots_bypipe(self):
            fu = bot.futr
            if not (fu.done() or  fu.cancelled()) and bot.idle == False:
                return False
        return True

    def __call__(self, list):
        pass

    def __repr__(self):
        return 'Pip_' + str(id(self))




#note drivedn by data
class Timer(Route):
    def __init__(self, delay=1, max_time=None, until=None):

        # \|/
        #  |
        #  |

        self.delay = delay
        self.max_time = max_time
        self.until = until


    def make_route_bot(self, iq,oq):
        self.outer_oq=oq
        self.outer_iq=iq
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

    def make_route_bot(self,iq,oq):



        q_o = queue.DataQueue()
        self.outer_iq=iq
        self.outer_oq=oq

        self.start_q=[q_o]
        self.output_q=queue.DataQueue()
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

    async def route_out(self):
        return await self.output_q.get()
class Return(Route):


    def make_route_bot(self,iq,oq):
        self.share=False
        self.joined=True

        q_o = iq
        self.outer_iq=iq
        self.outer_oq=oq

        self.start_q=[q_o]
        self.output_q=oq
        # if self.share:
        #     self.start_q.append(oq)
        for idx,func in enumerate(self.args):
            q_i = q_o
            if  idx == len(self.args)-1:

                q_o = self.output_q

            else:
                q_o = queue.DataQueue()



            BotFrame.make_bot(q_i, q_o, func)


class Loop(Route):

    def make_route_bot(self,iq,oq):
        self.share=False
        self.joined=True

        self.outer_iq=iq
        self.outer_oq=oq


        q_o= queue.DataQueue()
        self.start_q = [q_o]
        # if self.share:
        #     self.start_q.append(oq)
        for idx,func in enumerate(self.args):
            q_i = q_o
            q_o = queue.DataQueue()

            BotFrame.make_bot(q_i, q_o, func)

        self.output_q=q_o


    def get_route_output_q_desc(self):
        return [self.outer_oq]+[self.outer_iq]+[self.output_q]

    async def route_in(self,data):
        await self.start_q[0].put(data)


    async def route_out(self):

        r=await self.output_q.get()
        await self.outer_iq.put(r) ##Loop to start q
        return r



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


class SendTo(Route):

    def __init__(self,target_node):
        super().__init__()
        self.target_node=target_node
        self.lock=asyncio.Lock()
    def make_route_bot(self,iq,oq):


        self.share=False
        self.joined=True

        self.outer_iq=iq
        self.outer_oq=oq

        self.route_target_q=self.target_node.outer_iq

        self.start_q = [queue.DataQueue(maxsize=0)]
        self.output_q=oq


    def get_route_input_q_desc(self):
        return [self.outer_oq]+[self.route_target_q]+self.start_q
    flag=0
    async def route_in(self,data):

        await self.route_target_q.put(data)

        #
        # #async with self.lock:
        #     await self.start_q[0].put(data)
        #
        #     start_q=self.start_q[0]
        #     #print("start q id {} rate {}".format(id(start_q), start_q.qsize()))
        #     maxsize = self.route_target_q.maxsize
        #
        #     while True:
        #         size = self.route_target_q.qsize()
        #
        #         # if size >110 and start_q.qsize() >110:
        #         #     #print('a')
        #         #     if self.flag==0:
        #         #         queue.QueueManager().debug()
        #         #         self.flag=1
        #          #   pass
        #
        #
        #         if  size/maxsize > 0.9 or self.start_q[0].qsize()  ==0 :
        #             break
        #         #print("trage q id {} rate {},{}".format(id(self.route_target_q),size / maxsize,size))
        #         r=await self.start_q[0].get()
        #         await self.route_target_q.put(r)  ##Loop to start q



    async def route_out(self):

        raise Exception("should not be called")



class Join(Route):

    def __init__(self, *args, merge_node=None):

        super(Route, self).__init__()

        self.route_type = [object]
        self.route_func = None
        self.merge_node = merge_node
        self.args = args
        self.databoard = Databoard()



    def make_route_bot(self,iq,oq):
        self.outer_iq=iq
        self.outer_oq=oq

        if self.merge_node is None:
            self.make_route_bot_join(oq)
        else:
            self.make_route_bot_joinmerge(oq)


    async def route_in(self,bdata):
        if self.merge_node is None:
            new_data=Bdata(bdata.data, bdata)
            await super().route_in(new_data)
        else:
            await self.route_in_joinmerge(bdata)


    def make_route_bot_join(self,oq):
        self.share = False
        self.joined=True
        self.route_type=[object]

        if self.joined:
            q_o = oq
        else:
            q_o = queue.NullQueue()

        self.start_q = []
        self.output_q = oq


        for func in self.args:
            q_i = queue.DataQueue()
            self.start_q.append(q_i)
            BotFrame.make_bot(q_i, q_o, func)

    def make_route_bot_joinmerge(self, oq):

        self.start_q = []
        self.output_q = oq
        self.merge_q = queue.DataQueue()
        self.inner_output_q = queue.DataQueue()

        self.share = False
        self.joined = True
        self.raw_bdata = True
        self.count = 0

        for func in self.args:
            i_q = queue.DataQueue()
            self.start_q.append(i_q)
            BotFrame.make_bot(i_q, self.output_q, func)






    async def route_in_joinmerge(self, bdata):

        if bdata.is_BotControl():
            await super().route_in(bdata)

        else:

            data = Bdata(bdata.data, bdata)
            data.count = 0
            await super().route_in(data)

            r = await self.databoard.wait_ori(bdata)
            await self.merge_node.put_result(r)
            self.databoard.drop_ori(bdata)




class Merge(Route):

    def __init__(self,pair=None):
        super().__init__()
        self.pair=pair
        self.future_list=[]
        self.join_node=None

    def make_route_bot(self,iq,oq):
        self.start_q=[oq]
        self.output_q=oq
        self.share=False
        self.joined=False
        self.outer_iq=iq
        self.outer_oq=oq


    def get_output_q(self):
        return self.output_q
    async def route_in(self, bdata):

        bdata.incr()
        self.databoard.set_ack(bdata)
        if bdata.is_BotControl():
            await self.output_q.put(bdata)



    async def put_result(self,result):

        await self.output_q.put(Bdata.make_Bdata_zori(result))


#
# class BlockedJoin(Route):
#
#
#
#
#     def __init__(self,*args,merge_node=None):
#
#
#         super(Route, self).__init__()
#
#         self.route_type=[object]
#         self.route_func=None
#         self.merge_node=merge_node
#         self.args=args
#         self.databoard=Databoard()
#
#
#     def make_route_bot(self,oq):
#
#         self.start_q = []
#         self.output_q=oq
#         self.merge_q=queue.DataQueue()
#         self.inner_output_q=queue.DataQueue()
#         null=queue.DataQueue()
#         self.share = False
#         self.joined=True
#         self.raw_bdata = True
#         self.count=0
#
#
#         self.start_index = len(BotFrame.bots)
#         for func in self.args:
#
#             i_q = queue.DataQueue()
#             self.start_q.append(i_q)
#             BotFrame.make_bot(i_q, self.output_q, func)
#
#         #self.merge_route=Merge(pair=self)
#         #BotFrame.make_bot(self.inner_output_q,self.output_q,self.merge_route)
#
#
#
#         self.end_index = len(BotFrame.bots)
#
#
#
#     def callback(self,fut):
#         print(fut._result)
#         self.merge_route.put_result(fut._result)
#
#
#     async def route_in(self,bdata):
#
#
#
#         if bdata.is_BotControl():
#             await super().route_in(bdata)
#
#         else:
#
#             data=Bdata(bdata.data,bdata)
#             data.count=0
#             await super().route_in(data)
#             # f=asyncio.ensure_future(self.databoard.wait_ori(bdata))
#             # self.merge_route.future_list.append(f)
#            #f=self.databoard.create_future(data.ori,self.callback)
#             #self.merge_route.future_list.append(f)
#             r = await self.databoard.wait_ori(bdata)
#             await self.merge_node.put_result(r)
#             self.databoard.drop_ori(bdata)















        # def init_param(self):
        #     self.raw_bdata=True
        # async def __call__(self,bdata):
        #         #await self.inner_output_q.get()
        #         parent=self.kwargs['parent']
        #         parent.joined_result[bdata.ori].append(bdata.data)
        #         if len(parent.joined_result[bdata.ori]) == len(parent.args):
        #             #del self.joined_result[bdata.ori]
        #             await parent.output_q.put(Bdata(parent.joined_result[bdata.ori],ori=bdata.ori))


    # def get_route_output_q_desc(self):
    #
    #     return  [self.inner_output_q]















###########short name ############

F = Fork
Fi=Filter
J = Join
P = Pipe
B = Branch
T = Timer