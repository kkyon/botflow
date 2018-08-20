# modified fetch function with semaphore
import random
import asyncio
from aiohttp import ClientSession
import aiohttp
from databot.flow import Pipe,Passby,Branch,Timer
from databot.bot import Bot

from dataclasses import dataclass
from functools import partial
from databot.httploader import HttpLoader
import logging
logging.basicConfig(level=logging.DEBUG)


def main():



    #make data flow net
    Pipe(
            Timer(delay=0.5,max_time=10),print


             )


    Bot.run()




main()



