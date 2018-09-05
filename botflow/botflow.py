import asyncio
from . import route
from .config import config
import logging
from .botbase import BotManager
from .queue import NullQueue, QueueManager
from .base import BotExit


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
    async def check_stop(cls):
        bm = BotManager()
        all_q = bm.get_all_q()
        while True:

            # await  config.main_lock.acquire()
            stop = True
            for bot in bm.get_bots():
                if len(bot.sub_task) != 0:
                    # print("{} {}".format(id(bot),len(bot.sub_task)))
                    stop = False
                    break

            for q in all_q:
                if isinstance(q, NullQueue):
                    continue
                if q.empty() == False:
                    # print("id:{} size:{}".format(id(q),q.qsize()))
                    stop = False
                    break

            if stop:
                break

            await asyncio.sleep(2)

        for bot in bm.get_bots():
            bot.stoped = True
        logging.info("ready to exit")
        for q in all_q:
            for get in q._getters:
                get.set_exception(BotExit("Bot exit now"))

    @classmethod
    def run(cls):

        if config.replay_mode:
            try:
                route.Pipe.restore_for_replay()
            except:
                raise

        bot_nodes = []
        bots = BotManager().get_bots()
        for b in bots:
            # if not b.stoped:
            if b.main_coro is not None:
                task = asyncio.ensure_future(b.main_coro)
                b.main_task = task
                bot_nodes.append(task)

        if len(bot_nodes) != len(set(bot_nodes)):
            raise Exception("")
        logging.info('bot number %s', len(bots))
        try:
            # asyncio.get_event_loop().run_forever()
            pipe_loop = asyncio.ensure_future(cls.check_stop())
            bot_nodes.append(pipe_loop)
            f = asyncio.gather(*bot_nodes)

            asyncio.get_event_loop().run_until_complete(f)


        except Exception as e:
            if config.replay_mode:
                route.Pipe.save_for_replay()
                raise e

            else:
                raise e

    @classmethod
    def debug_print(cls):
        BotManager().debug_print()
        QueueManager().debug_print()
        # Databoard().debug_print()

    @classmethod
    def enable_debug(cls):
        config.debug = True
