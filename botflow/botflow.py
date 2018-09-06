import asyncio
from .config import config
import logging
from .botbase import BotManager
from .queue import NullQueue, QueueManager
from .base import BotExit
from aiohttp.web import AppRunner,TCPSite
from .route import Pipe

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

    @classmethod
    async def check_stop(cls):
        bm = BotManager()
        all_q = bm.get_all_q()

        while True:

            # await  config.main_lock.acquire()
            stop=True
            for bot in bm.get_bots():
                if len(bot.sub_task) != 0:
                    logging.debug("{} {}".format(id(bot),len(bot.sub_task)))
                    stop = False
                    break

            for q in all_q:
                if isinstance(q, NullQueue):
                    continue
                if q.empty() == False:
                    print("id:{} size:{}".format(id(q),q.qsize()))
                    logging.debug("id:{} size:{}".format(id(q),q.qsize()))
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
        bot_nodes = []
        bots = BotManager().get_bots()
        for b in bots:
            # if not b.stoped:
            if b.main_coro is not None:
                task = asyncio.ensure_future(b.main_coro)
                b.main_task = task
                bot_nodes.append(task)
        return bot_nodes


    @classmethod
    def run_app(cls,app,host='0.0.0.0', port=8080):

        config.never_stop = True

        bot_nodes=cls.start()
        bm = BotManager()

        app_task = asyncio.ensure_future(cls.run_web_app(app,host,port))
        bot_nodes.append(app_task)

        f = asyncio.gather(*bot_nodes)

        asyncio.get_event_loop().run_until_complete(f)



    @classmethod
    def run(cls):

        if config.replay_mode:
            try:
                Pipe.restore_for_replay()
            except:
                raise

        bot_nodes=cls.start()
        bm = BotManager()






        if len(bot_nodes) != len(set(bot_nodes)):
            raise Exception("")

        try:

            for p in bm.get_pipes():
                p.start()

            if not config.never_stop :
                pipe_loop = asyncio.ensure_future(cls.check_stop())
                bot_nodes.append(pipe_loop)
            f = asyncio.gather(*bot_nodes)

            asyncio.get_event_loop().run_until_complete(f)


        except Exception as e:
            if config.replay_mode:
                Pipe.save_for_replay()
                raise e

            else:
                raise e

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
