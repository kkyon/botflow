import asyncio
from .config import config
import logging
from .botbase import BotManager
from .queue import SinkQueue, QueueManager,DataQueue,ConditionalQueue
from .base import BotExit,get_loop,_BOT_LOOP
from aiohttp.web import AppRunner,TCPSite
from .pipe import Pipe
from .botframe import BotFrame
from .bdata import Bdata

logger = logging.getLogger(__name__)
class MyEventLoopPolicy(asyncio.DefaultEventLoopPolicy):

    def get_event_loop(self):
        # Do something with loop ...
        return _BOT_LOOP

class BotFlow(object):



    started=False
    @classmethod
    def render(cls, filename):
        from graphviz import Digraph
        f = Digraph(comment=__file__, format='png')
        f.attr('node', shape='circle')
        cls.start()
        cls.started=True
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
    async def run_web_app(cls,app,host,port):
        runner = AppRunner(app)
        await runner.setup()
        site = TCPSite(runner, host,port)
        await site.start()




    @classmethod
    def start(cls):
        if cls.started:
            return
        pipes = BotManager().get_pipes()
        for p in pipes:
            start_q=DataQueue()
            end_q=ConditionalQueue()
            p._make(start_q,end_q)
            p._start()




    @classmethod
    def run_app(cls,app,host='0.0.0.0', port=8080):

        asyncio.set_event_loop_policy(MyEventLoopPolicy())
        print(f"BotFlow start web server http://{host}:{port}")
        config.never_stop = True

        cls.start()

        asyncio.ensure_future(cls.run_web_app(app,host,port))



        get_loop().run_forever()



    @classmethod
    def run(cls,*pipes,silent=False,render=None):


        bm=BotManager()
        loop=get_loop()
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
            if len(pipes) == 0:
                pipes=bm.get_pipes()
            for p in pipes:
                start_q=DataQueue()
                end_q  =SinkQueue()
                p._make(start_q,end_q)
                p._start()
                bdata=Bdata.make_Bdata_zori(0)
                task=get_loop().create_task(p._true_run(bdata))
                tasks.append(task)

            f = asyncio.gather(*tasks,loop=loop)

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
