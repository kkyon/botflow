import asyncio
import logging
from .botframe import BotFrame
from .config import config

from .queue import DataQueue,SinkQueue,CachedQueue,ProxyQueue,ConditionalQueue,QueueManager
from botflow.bdata import Bdata,Databoard
from .botbase import BotManager
from .routebase import Route
from .botflow import BotFlow
import sys
# main pipe

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







class Branch(Route):

    def is_last_one(self, list, item):
        if item == list[-1]:
            return True
        else:
            return False

    def make_route_bot(self,iq,oq):



        q_o = DataQueue()
        self.outer_iq=iq
        self.outer_oq=oq

        self.start_q=[q_o]
        self.output_q=DataQueue()
        # if self.share:
        #     self.start_q.append(oq)
        for idx,func in enumerate(self.args):
            q_i = q_o
            if  idx == len(self.args)-1:
                if self.joined :
                    q_o = self.output_q
                else:
                    q_o = SinkQueue()
            else:
                q_o = DataQueue()



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
                q_o = DataQueue()



            BotFrame.make_bot(q_i, q_o, func)

Line=Return

class Loop(Route):

    def make_route_bot(self,iq,oq):
        self.share=False
        self.joined=True

        self.outer_iq=iq
        self.outer_oq=oq


        q_o= DataQueue()
        self.start_q = [q_o]
        # if self.share:
        #     self.start_q.append(oq)
        for idx,func in enumerate(self.args):
            q_i = q_o
            q_o = DataQueue()

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
            q_o = SinkQueue()

        self.start_q = []
        self.output_q = oq

        #parallel in sub network not in node
        for func in self.args:
            q_i = DataQueue()
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

        self.start_q = [DataQueue()]
        self.output_q=oq


    def routein_out_q(self):
        return [self.route_target_q]
    def get_route_input_q_desc(self):
        return [self.outer_oq]+[self.route_target_q]+self.start_q
    flag=0
    async def route_in(self,data):

        await self.route_target_q.put(data)




    async def route_out(self):

        raise Exception("should not be called")


Link=SendTo

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
            if bdata.ori ==0:
                new_data=Bdata(bdata.data, bdata)
                await super().route_in(new_data)
            else:
                await super().route_in(bdata)
        else:
            await self.route_in_joinmerge(bdata)


    def make_route_bot_join(self,oq):
        self.share = False
        self.joined=True
        self.route_type=[object]

        if self.joined:
            q_o = oq
        else:
            q_o = SinkQueue()

        self.start_q = []
        self.output_q = oq


        for func in self.args:
            q_i = DataQueue()
            self.start_q.append(q_i)
            BotFrame.make_bot(q_i, q_o, func)

    def make_route_bot_joinmerge(self, oq):

        self.start_q = []
        self.output_q = oq
        self.merge_q = DataQueue()
        self.inner_output_q = DataQueue()

        self.share = False
        self.joined = True
        self.raw_bdata = True
        self.count = 0

        for func in self.args:
            i_q = DataQueue()
            self.start_q.append(i_q)
            BotFrame.make_bot(i_q, self.output_q, func)






    async def route_in_joinmerge(self, bdata):

        # if bdata.is_BotControl():
        #     await super().route_in(bdata)
        #
        # else:

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
        # if bdata.is_BotControl():
        #     await self.output_q.put(bdata)



    async def put_result(self,result):

        await self.output_q.put(Bdata.make_Bdata_zori(result))














###########short name ############

F = Fork
J = Join
B = Branch
T = Timer