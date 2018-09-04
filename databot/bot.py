
from .botframe import BotFrame
from .botbase import BotManager
from .config import config
from .queue import QueueManager
from .bdata import Databoard

class Bot(object):

    @classmethod
    def stop_forece(cls):
        exit(-1)

    @classmethod
    def run(cls):
        BotFrame.run()

    @classmethod
    def render(cls, filename):
        BotFrame.render(filename)

    @classmethod
    def debug_print(cls):
        BotManager().debug_print()
        QueueManager().debug_print()
        Databoard().debug_print()


    @classmethod

    def enable_debug(cls):
        config.debug=True


