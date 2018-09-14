import asyncio
import logging
from .botframe import BotFrame
from .config import config
from .base import get_loop
from .queue import DataQueue,SinkQueue,CachedQueue,ProxyQueue,ConditionalQueue,QueueManager
from botflow.bdata import Bdata,Databoard
from .botbase import BotManager
from .routebase import Route
from .botflow import BotFlow
import sys
# main pipe

#note drivedn by data
__all__=["Timer","Tee","Link","Zip","Join"]
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







class Tee(Route):

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


Branch=Tee

class Link(Route):

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





class Zip(Route):

    def __init__(self, *args, merge_node=None):

        super(Route, self).__init__()

        self.route_type = [object]
        self.route_func = None
        self.args = args
        self.share=False
        self.joined=True
        self.loop=get_loop()

        self.databoard = Databoard()
        self.lock=asyncio.Event(loop=get_loop())
        self.ori_list=DataQueue(maxsize=0)

    def routeout_in_q(self):
        r=super().routeout_in_q()
        r.append(self.ori_list)
        return r


    def make_route_bot(self,iq,oq):
        self.outer_iq=iq
        self.outer_oq=oq



        self.start_q = []
        self.output_q = []


        # self.output_q = q_o
        for func in self.args:
            q_i = DataQueue()
            q_o = ConditionalQueue()
            self.start_q.append(q_i)
            self.output_q.append(q_o)
            BotFrame.make_bot(q_i, q_o, func)




    async def route_in(self,bdata):

        await self.ori_list.put(bdata)

        new_bdata=Bdata(bdata.data,bdata)
        for q in self.start_q:
            await q.put(new_bdata)




    async def route_out(self):


        o=await self.ori_list.get()
        result=[]
        for q in self.output_q:
            try:
                r=await q.get_by(o)
                result.append(r.data)
                # task=self.loop.create_task(q.get_by(o))
                # tasks.append(task)
            except Exception as e:
                logging.exception("excd")

        # r=await asyncio.gather(*tasks,get_loop())
        return Bdata(result,o)



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
            if bdata.ori.ori ==0:
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











###########short name ############

J = Join
B = Branch
T = Timer