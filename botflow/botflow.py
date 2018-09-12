import asyncio
from .config import config
import logging
from .botbase import BotManager
from .queue import SinkQueue, QueueManager,DataQueue,ConditionalQueue
from .base import BotExit,get_loop
from aiohttp.web import AppRunner,TCPSite
from .pipe import Pipe
from .botframe import BotFrame
from .bdata import Bdata

logger = logging.getLogger(__name__)
class BotFlow(object):



    @classmethod
    def render(cls, filename):
        from graphviz import Digraph
        f = Digraph(comment=__file__, format='png')
        f.attr('node', shape='circle')

        bots = BotManager().get_bots()
        for idx, b in enumerate(bots):
            name = str(b.func).replace('>', '').replace('<', '')
            name = name.split('.')[-1]
            name = name.split('at')[0]
            name = "(%d)" % (idx) + name
            f.node(str(id(b)), name)
            bid = str(id(b))
            for p in b.parents:
                pid = str(id(p))
                f.edge(pid, bid)

        f.render(filename, view=True)

    @classmethod
    def stop(cls,force=False):
        bm = BotManager()
        all_q = bm.get_all_q()
        for bot in bm.get_bots():
            bot.stoped = True

        for q in all_q:
            for get in q._getters:
                get.set_exception(BotExit("Bot exit now"))
        cls.stopped=True
        bm.loop.stop()

    @classmethod
    async def check_stop(cls):
        bm = BotManager()
        all_q = bm.get_all_q()

        while True:

            # await  config.main_lock.acquire()
            stop=True
            if logger.level == logging.DEBUG:
                QueueManager().debug_print()
            #QueueManager().debug_print()
            for bot in bm.get_bots():
                if len(bot.sub_task) != 0:
                    logger.debug("bot id :{} sub task len:{} sopt to close".format(id(bot),len(bot.sub_task)))
                    stop = False
                    break

            for q in all_q:
                if isinstance(q, SinkQueue):
                    continue
                if q.empty() == False:
                    #print("id:{} size:{}".format(id(q),q.qsize()))
                    logger.debug("id:{} size:{} stop to close".format(id(q),q.qsize()))
                    stop = False
                    break

            if stop and config.check_stoping :
                break

            await asyncio.sleep(2)

        logging.info("ready to exit")
        cls.stop()

    @classmethod
    async def run_web_app(cls,app,host,port):
        runner = AppRunner(app)
        await runner.setup()
        site = TCPSite(runner, host,port)
        await site.start()




    @classmethod
    def start(cls):
        tasks = []
        pipes = BotManager().get_pipes()
        for p in pipes:
            start_q=DataQueue()
            end_q=ConditionalQueue()
            tasks.append(p._make_and_start(start_q,end_q))

        return tasks


    @classmethod
    def run_app(cls,app,host='0.0.0.0', port=8080):

        print(f"BotFlow start web server http://{host}:{port}")
        config.never_stop = True

        bot_nodes=cls.start()

        app_task = asyncio.ensure_future(cls.run_web_app(app,host,port))
        bot_nodes.append(app_task)

        f = asyncio.gather(*bot_nodes)

        get_loop().run_until_complete(f)



    @classmethod
    def run(cls,*pipes,silent=False,render=None):


        bm=BotManager()
        if render is not None:
            cls.render(render)
        if not silent :
            QueueManager().dev_mode()

        if config.replay_mode:
            try:
                Pipe.restore_for_replay()
            except:
                raise

        try:

            tasks=[]
            if pipes is None:
                pipes=bm.get_pipes()
            for p in pipes:
                start_q=DataQueue()
                end_q  =SinkQueue()
                bdata=Bdata.make_Bdata_zori(0)
                task=get_loop().create_task(p._true_run(start_q,end_q,bdata))
                tasks.append(task)

            f = asyncio.gather(*tasks)

            get_loop().run_until_complete(f)


        except Exception as e:
            if config.replay_mode:
                Pipe.save_for_replay()
                raise e

            else:
                raise e
        finally:
            BotFlow.reset()

    @classmethod
    def reset(cls):

        BotManager().rest()

    @classmethod
    def debug_print(cls):
        BotManager().debug_print()
        QueueManager().debug_print()
        # Databoard().debug_print()

    @classmethod
    def enable_debug(cls):
        config.debug = True
