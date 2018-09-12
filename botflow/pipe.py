import asyncio
import logging
from .botframe import BotFrame
from .config import config

from .queue import DataQueue,SinkQueue,CachedQueue,ProxyQueue,ConditionalQueue,QueueManager
from botflow.bdata import Bdata,Databoard
from .botbase import BotManager
from .routebase import Route
from .base import BotExit

import sys
import logging
logger=logging.getLogger(__name__)


class Runnable(object):
    def stop(self, force=False):
        bm = BotManager()

        for bot in bm.get_bots_bypipe(self):
            bot.stoped = True

        for q in self.all_q:
            for get in q._getters:
                get.set_exception(BotExit("Bot exit now"))

    async def check_stop(self):

        all_q = self.all_q

        while True:

            # await  config.main_lock.acquire()
            stop = True
            if logger.level == logging.DEBUG:
                QueueManager().debug_print()
            # QueueManager().debug_print()
            for bot in self.bm.get_bots_bypipe(self):
                if len(bot.sub_task) != 0:
                    logger.debug("bot id :{} sub task len:{} sopt to close".format(id(bot), len(bot.sub_task)))
                    stop = False
                    break

            for q in all_q:
                if isinstance(q, SinkQueue) or self.output_q == q:
                    continue
                if q.empty() == False:
                    # print("id:{} size:{}".format(id(q),q.qsize()))
                    logger.debug("id:{} size:{} stop to close".format(id(q), q.qsize()))
                    stop = False
                    break

            if stop and config.check_stoping:
                break

            await asyncio.sleep(2)

        logging.info("pipe_{} ready to exit".format(id(self)))
        self.stop()



    def get_start_q(self):
        return self.start_q[0]

    async def run_async(self, data):

        ori = Bdata.make_Bdata_zori(data)
        await self.get_start_q().put(Bdata(data, ori))
        r = await self.output_q.get_by(ori)
        self.output_q.clean(ori)
        if isinstance(r.data, list):
            for i, v in enumerate(r.data):
                if isinstance(v, Exception):
                    r.data[i] = None
        return r.data


    def _start(self):


        bots = BotManager().get_bots_bypipe(self)
        tasks = []
        for b in bots:
            # if not b.stoped:
            if b.main_coro is not None:
                task = self.bm.loop.create_task(b.main_coro)
                b.main_task = task
                tasks.append(task)

        return tasks
    def _make(self,start_q,end_q):

        self.make_route_bot(start_q, end_q)

    async def _true_run(self,  bdata):


        await self.get_start_q().put(bdata)
        await self.check_stop()

    def run(self, data):

        start_q = DataQueue()
        end_q = DataQueue()
        bdata = Bdata.make_Bdata_zori(data)
        self._make(start_q,end_q)
        self._start()
        self.bm.loop.run_until_complete(self._true_run(bdata))
        result = []
        while True:
            try:
                r = self.output_q.get_nowait()
                result.append(r.data)
            except:
                break
        self.bm.loop.stop()
        return result

class Pipe(Runnable,Route):

    # |
    # |
    # |
    # |

    def __init__(self, *args):
        self.bm=BotManager()
        q_o = DataQueue()
        self.route_type = [object]
        self.route_func=None
        # get this pip own inside bot

        self.bot_start_index=0
        self.bot_end_index=0

        self.joined = False
        self.args=args
        self.bots=[]
        BotManager().add_pipes(self)


    def make_route_bot(self,iq,oq):
        self.share=False
        self.outer_iq = iq
        self.outer_oq = oq




        self.bot_start_index = len(self.bm.get_bots())
        self.start_q = [iq]
        q_o=self.start_q[0]
        for idx, func in enumerate(self.args):
            q_i = q_o
            if idx == len(self.args) - 1:
                q_o = oq

            else:
                if config.replay_mode:
                    q_o = CachedQueue()
                else:
                    q_o = DataQueue()

            bis = BotFrame.make_bot(q_i, q_o, func)
            for b in bis:
                b.flow = 'main'


        self.bot_end_index = len(self.bm.get_bots())
        self.output_q = q_o
        bots = self.bm.get_bots()

        self.all_q = set()
        for i in range(self.bot_start_index, self.bot_end_index):
            bot = bots[i]
            self.bots.append(bot)
            bot.pipeline = self
            for q in bot.iq:
                self.all_q.add(q)
            for q in bot.oq:
                self.all_q.add(q)


        self.bm.make_bot_flowgraph(self)







    async def aiohttp_json_handle(self,request):

        from aiohttp import web
        r = await self.run_async(request)
        return web.json_response(r)


    def sanic_json_handle(self):
        from sanic.response import json
        async def _wrap(request):
            r = await self(request)
            return json(r)

        return _wrap



    @classmethod
    def empty(cls):
        bm=BotManager()
        bi=bm.get_botinfo_current_task()
        for q in bi.pipeline.all_q:
            if isinstance(q, SinkQueue):
                continue
            if q.empty() == False:
                print("id:{}".format(id(q)))
                return False


        for bot in bm.get_bots_bypipe(bi.pipeline):

            if bi == bot:
                continue
            if len(bot.sub_task) !=0:
                print(bot.func,bot,len(bot.sub_task))
                return False




        return True

    def  save_for_replay(self):
        '''it will save cached data for pay back'''

        self.pickle_name = sys.modules['__main__'].__file__ + 'palyback.pk'
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
            task = bot.main_task
            if not (task.done() or  task.cancelled()) and bot.idle == False:
                return False
        return True

    async def write(self,data):
        await self.start_q.put(Bdata.make_Bdata_zori(data))

    async def read(self):
        r =await self.output_q.get()
        yield r

        while not self.output_q.empty():
            r=self.output_q.get_nowait()
            yield r




    def dev_mode(self):
        QueueManager().dev_mode()
    def __call__(self, data):

        return self.run(data)




    def __repr__(self):
        return 'Pip_' + str(id(self))



