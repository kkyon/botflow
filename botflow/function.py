from .functionbase import Function
from .botframe import BotFrame
from .bdata import Bdata
from .base import flatten,get_loop
import asyncio

import datetime



import typing

class Flat(Function):

    def __init__(self,level=0):
        super().__init__()
        self.level=0
        self.raw_bdata=True

    def __call__(self, bdata):
        if isinstance(bdata.data, (list,typing.Generator)):

            for i in bdata.data:
                yield i

        else:

            yield bdata.data




# class SendTo(Node):
#
#     def __init__(self,node):
#         super().__init__()
#         self.node=node
#         self.target_q=None
#         self.raw_bdata=True
#
#     def init(self):
#
#         b=BotFrame.bots[self.node_id]
#         # self.target_q=b.iq[0]
#         # return b.iq[0]
#
#     def get_target_q(self):
#         if self.target_q is not None:
#             return self.target_q
#
#         self.target_q=self.node.outer_iq
#         return self.target_q
#         # b=BotFrame.bots[self.node_id]
#         # self.target_q=b.iq[0]
#         # return b.iq[0]
#
#     async def __call__(self, message,route_type=object):
#
#         #get input q of node
#         q=self.get_target_q()
#         await q.put(message)


class Zip(Function):
    def __init__(self,n_stream=0):
        if  n_stream == 0:
            raise Exception('for Zip node ,need to set join_ref or n_stream')

        super().__init__()
        #self.join_ref=join_ref
        self.n_stream=n_stream
        self.buffer={}
        self.raw_bdata=True


    # def init(self):
    #self.n_stream=self.join_ref.n_stream
    #     return

    async def __call__(self, bdata):
        if bdata.ori not in self.buffer:
            self.buffer[bdata.ori] = []

        self.buffer[bdata.ori].append(bdata.data)

        if len(self.buffer[bdata.ori]) == self.n_stream:
            return self.buffer[bdata.ori]



class Filter(Function):


    def __init__(self, filter_types=None,filter_func=None):
        super().__init__()
        if not isinstance(filter_types,list) and filter_types is not None:
            filter_types=[filter_types]

        self.filter_types=filter_types
        self.filter_func=filter_func

    async def __call__(self, data):

        matched=False
        if self.filter_types:
            for t in self.filter_types:
                if isinstance(data,t):
                    matched=True
                    break
        else:
            matched=True

        if matched and (self.filter_func == None or self.filter_func(data)):
            return data


class Delay(Function):
    def __init__(self,delay_time=1):
        super().__init__()
        self.delay_time=delay_time
        self.lock=asyncio.Lock(loop=get_loop())

    async def __call__(self,data):
        await self.lock.acquire()
        await asyncio.sleep(self.delay_time)
        self.lock.release()
        return data

class SpeedLimit(Function):
    def __init__(self,speed):
        super().__init__()
        self.processed_count=0
        self.start_time=datetime.datetime.now()
        self.speed_limit=speed
        self.lock=asyncio.Lock()

    async def __call__(self,data):
        self.processed_count += 1
        if self.processed_count > self.speed_limit:
            await self.lock.acquire()
            end = datetime.datetime.now()
            s=(end-self.start_time).total_seconds()
            speed_now=self.processed_count/s
            if speed_now>(self.speed_limit*1.1) :
                sleep_time=self.processed_count/self.speed_limit-s
                self.start_time = datetime.datetime.now()
                await asyncio.sleep(sleep_time)
            else:
                self.start_time = datetime.datetime.now()
            self.processed_count=0

            self.lock.release()

        return data

def print_list(d:list):
    print(d)
    return d
