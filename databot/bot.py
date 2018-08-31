from databot.botframe import BotFrame

from databot.flow import Pipe,Timer,Branch,Join,Filter,Fork
from databot.node import Node
from databot.db.aiofile import aiofile
from databot.botframe import BotFrame
from databot.http.http import HttpRequest,HttpLoader,HttpResponse


class Bot(object):

    @classmethod

    def run(cls):
        BotFrame.run()


    @classmethod

    def render(cls,filename):
        BotFrame.render(filename)


    @classmethod

    def debug(cls):
        BotFrame.debug()