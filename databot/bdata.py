from .base import CountRef,Singleton

import asyncio
import logging

import uuid

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


DATA_ADD=1
DATA_REMOVE=2
DATA_COMPLETE=3

class Databoard(object,metaclass=Singleton):




    def __init__(self):
        self._datatrack = {}
        self._futures = {}
        self.debug=True
        #self.buffer=[]

        # self.buffer=[]
    def debug_print(self):
        for k,v in self._datatrack.items():
            if type(k) == int:
                print("Databoard datatrack {},len:{}".format(k))
            else:
                print("Databoard datatrack {},len:{}".format(k,len(v)))
        for k,v in self._futures.items():
            print("Databoard future {},len:{}".format(k,len(v)))
    def check_compeleted(self,ori):
        for k, v in self._datatrack[ori].items():
            if v == DATA_ADD:
                return False

        result = []
        for k, v in self._datatrack[ori].items():
            if v == DATA_COMPLETE:
                result.append(k.data)

        return result



    def _check_aweak(self, ori):

        if ori not in self._futures:
            return
        result=self.check_compeleted(ori)
        if result== False:
            return
        else:


            if not self._futures[ori].done():
                self._futures[ori].set_result(result)

            return True

    def add(self, bdata):


        if bdata.ori == 0 or bdata.ori.ori == 0 or bdata.is_BotControl():
            return
        #self.buffer.append(bdata)
        ori = bdata.ori
        data = bdata.data

        if ori not in self._datatrack:
            self._datatrack[ori] = {}
        self._datatrack[ori][bdata] = DATA_ADD



    def remove(self, bdata):

        if bdata.ori == 0 or bdata.is_BotControl() or bdata.ori not in self._datatrack:
            return

#        logging.DEBUG("remove %s",bdata)
        ori = bdata.ori
        data = bdata.data
        if self._datatrack[ori][bdata] != DATA_COMPLETE:
            self._datatrack[ori][bdata] = DATA_REMOVE
        self._check_aweak(ori)

    def get_status(self, ori, bdata):
        return self._datatrack[ori][bdata]

    def set_ack(self, bdata):
        if bdata.ori == 0 or bdata.is_BotControl():
            return

        ori = bdata.ori
        data = bdata.data
        try:
            self._datatrack[ori][bdata] = DATA_COMPLETE
        except:
            raise
        self._check_aweak(ori)


    def get_future(self,ori):

        return self._futures[ori]


    def create_future(self,ori,callback):

        if ori == 0:
            raise Exception("can't wait for 0 input")
            return
        future = asyncio.get_event_loop().create_future()
        future.add_done_callback(callback)
        self._futures[ori] = future
        return future

    async def wait_ori(self, ori):
        if ori == 0 or ori in self._futures:
            raise Exception("can't wait for 0 input")
            return
        future = asyncio.get_event_loop().create_future()
        self._futures[ori] = future

        return await future
        # return future.get_result()

    def drop_ori(self, ori):

        if ori in self._datatrack:
            del self._datatrack[ori]
            del self._futures[ori]




class Bdata(CountRef):


    qid=0
    @classmethod
    def get_uid(cls):
        cls.qid+=1
        return cls.qid


    __slots__ = ['_ori', '_data', '_meta', '_databoard','uid']

    def __init__(self, data, ori=None):
        super().__init__()
        if isinstance(data, Bdata) or (ori!=0 and not isinstance(ori,Bdata)) :
            raise Exception('not right data ' + str(data))
        self.uid=self.get_uid()
        self._data = data
        self._meta = None
        self._ori = ori
        self._databoard = Databoard()

        self.incr()
        self._databoard.add(self)

    def __repr__(self):
        if type(self.ori) == int:
            return "uid:{},count:{},ori:int({}):data:".format(self.uid, self.count, self.ori, self._data)
        else:
            return "uid:{},count:{},ori:{}:data:".format(self.uid,self.count,self.ori.uid,self._data)

    def __hash__(self):

        return self.uid

    def __eq__(self, other):
        if not hasattr(other,'uid'):
            return False

        return self.uid == other.uid

    def __ne__(self,other):
        if not hasattr(other, 'uid'):
            return True
        return not(self.uid == other.uid)


    def destroy(self):


        if self.decr() == 0:
            try:
                self._databoard.remove(self)
            except:
                raise


    @property
    def ori(self):
        return self._ori

    @property
    def data(self):
        return self._data

    def is_BotControl(self):

        return isinstance(self._data, BotControl)

    @classmethod
    def make_Retire(cls):
        return Bdata(Retire(),ZERO_DATA)

    @classmethod
    def make_Bdata_zori(cls,data):
        return Bdata(data, ZERO_DATA)

ZERO_DATA=Bdata(0,ori=0)