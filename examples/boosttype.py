import logging

logging.basicConfig(level=logging.DEBUG)
from botflow.config import config
config.default_queue_max_size=0

logging.debug(config)
from botflow import Pipe, Fork,Timer,Branch
from botflow import BotFlow
from botflow.node import Node
import time

#it will block whole main thread

@Node.boost
def very_slow(a):
    print('i am going to sleep')
    time.sleep(10)
    print('i am aweek')



def main():


    Pipe(
        Timer(delay=1,max_time=10),
        Branch(very_slow),
        print,

    )

    BotFlow.run()


main()
