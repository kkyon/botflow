
from databot.node import CountRef
import asyncio
import logging
class BotControl(object):
    pass


class Retire(BotControl):
    pass


class Suspend(BotControl):
    pass


class Resume(BotControl):
    pass


class ChangeIq(BotControl):

    def __init__(self, iq_num=128):
        self.iq_num = iq_num

class _BdataFrame(object):

    def __init__(self):
        self.datatrack={}
        self._futures={}
        #self.buffer=[]


    def _check_aweak(self,ori):


        if ori not in self._futures:
            return

        for k,v in self.datatrack[ori].items():
            if v == 'add':
                return False
        result=[]
        for k, v in self.datatrack[ori].items():
            if v == 'completed':
                result.append(k.data)



        if not self._futures[ori].done():
            self._futures[ori].set_result(result)

        return True

    def add(self,bdata):

        #self.buffer.append(bdata)
        ori=bdata.ori
        data=bdata.data

        if ori not in self.datatrack:
            self.datatrack[ori]={}
        self.datatrack[ori][bdata]='add'



    def remove(self,bdata):
        if bdata.ori == 0:
            return

        logging.debug("remove {}",bdata)
        ori = bdata.ori
        data = bdata.data
        if self.datatrack[ori][bdata] != 'completed':
            self.datatrack[ori][bdata] = 'remove'
        self._check_aweak(ori)


    def get_status(self,ori,bdata):
        return self.datatrack[ori][bdata]

    def set_ack(self,bdata):
        if bdata.ori == 0:
            return

        ori = bdata.ori
        data = bdata.data
        self.datatrack[ori][bdata] = 'completed'
        self._check_aweak(ori)


    async def wait(self,ori):
        if ori == 0:
            raise Exception("can't wait for 0 input")
            return
        future=asyncio.get_event_loop().create_future()
        self._futures[ori]=future

        return await future
        #return future.get_result()


    def drop_ori(self,ori):
        if ori in self.datatrack:
            del self.datatrack[ori]

BdataFrame=_BdataFrame()


class Bdata(CountRef):
    __slots__ = ['_ori','_data','_meta']

    def __init__(self,data,ori=0):
        super().__init__()
        if isinstance(data,Bdata):
            raise Exception('not right data '+str(data))
        self._data=data
        self._meta=None
        self._ori=ori


        self.incr()
        BdataFrame.add(self)

    def __repr__(self):
        return str(self.data)
    def destroy(self):

        if self.decr() ==0:
            BdataFrame.remove(self)




    @property
    def ori(self):
        return self._ori

    @property

    def data(self):
        return self._data

    def is_BotControl(self):

        return isinstance(self._data,BotControl)

    @classmethod
    def make_Retire(cls):
        return Bdata(Retire())