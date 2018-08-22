# modified fetch function with semaphore
from databot.flow import Pipe, Timer
from databot.botframe import BotFrame
from databot.http.http import FileSaver

import logging
logging.basicConfig(level=logging.DEBUG)


def main():




    Pipe(
            Timer(delay=0.5,max_time=10),

             FileSaver('a.txt')
             )


    BotFrame.run()




main()



