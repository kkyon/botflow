import asyncio
from .config import config
import logging
from .base import Singleton,list_included


class BotPerf(object):
    __slots__ = ['processed_number', 'func_avr_time', 'func_max_time', 'func_min_time']

    def __init__(self):
        self.processed_number = 0
        self.func_avr_time = None
        self.func_max_time = None
        self.func_min_time = None


class BotInfo(object):
    __slots__ = ['id','iq', 'oq', 'futr', 'task', 'func', 'route_zone', 'pipeline', 'stoped', 'perf', 'ep','idle',
                  'parents','flow']

    def __init__(self):
        self.id=0
        self.iq = []
        self.oq = []
        self.futr = None
        self.task = None
        self.func = None
        self.route_zone = None
        self.pipeline = None
        self.stoped = False
        self.idle=True
        self.flow=''
        self.perf = BotPerf()
        self.ep=config.Exception_default
        self.parents = []

    def __repr__(self):
        return str(id(self))




class BotManager(object,metaclass= Singleton):


    def __init__(self):
        self._bots=[]
        self_pipes=[]
        self.bot_id=0

    def new_bot_id(self):
        self.bot_id+=1
        return self.bot_id

    def add_bot(self,bi):
        if bi.id==0:
            bi.id=self.new_bot_id()
        self._bots.append(bi)

    def get_bots_bypipe(self,pipe):
        result=[]
        for b in self._bots:
            if b.pipeline==pipe:
                result.append(b)

        return result

    def make_bot_flowgraph(self,pipe):
        for bot in self.get_bots_bypipe(pipe):

            count = 0
            for bot_o in self.get_bots_bypipe(pipe):

                for q in bot_o.oq:
                    if list_included(bot.iq, q):

                        bot.parents.append(bot_o)



    def bots_size(self):
        return len(self._bots)

    def get_bots(self):
        return self._bots

    def get_reader_id_by_q(self,q):
        ids=[]
        for b in self._bots:
            if list_included(q,b.iq):
                ids.append(b.id)

        return ids
    def get_botinfo_by_id(self, id):
            for b in self._bots:
                if b.id == id:
                    return b
            return None


    def get_botinfo_current_task(self) -> BotInfo:
            task = asyncio.Task.current_task()
            for b in self._bots:
                if b.futr is task:
                    return b

    def make_bot_raw(self, iq, oq, f,fu):

        bi = BotInfo()
        bi.iq = iq
        if not isinstance(oq, list):
            oq = [oq]
        bi.oq = oq
        bi.futr = fu
        bi.func = f

        self._bots.append(bi)
    def debug_print(self):
        logging.info('-' * 50)
        for b in self._bots:

            if not isinstance(b.iq,list):
                b.iq=[b.iq]
            plist = ''
            for p in b.parents:
                plist += 'b_'+str(id(p)) + ','

            oq=''
            for q in b.oq:
                oq += 'q_'+str(id(q)) + ','

            iq=''
            for q in b.iq:
                iq += 'q_' + str(id(q)) + ','


            logging.info('%s,botid %s,pipe:%s,func:%s stoped:%s,parents:%s  ,iq:%s, oq:%s'% (b.id,b, b.pipeline, b.func, b.stoped,plist,iq,oq))
            #
            #

class PerfMetric(object):
    batch_size = 128
    suspend_time = 1

    def __init__(self):
        pass