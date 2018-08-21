# modified fetch function with semaphore
import random
import asyncio
from aiohttp import ClientSession
import aiohttp
from databot.flow import Pipe,Pass,Branch,Timer
from databot.botframe import BotFrame
from databot.httploader import FileSaver

from dataclasses import dataclass
from functools import partial
from databot.httploader import HttpLoader
import logging
logging.basicConfig(level=logging.DEBUG)


def main():




    Pipe(
            Timer(delay=0.5,max_time=10),

             FileSaver('a.txt')
             )


    BotFrame.run()




main()



