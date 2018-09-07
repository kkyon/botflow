
from botflow import *
import datetime
import logging
logger=logging.getLogger("botflow.queue")
#logger.setLevel(logging.DEBUG)
class SpeedTest:
    def __init__(self):

        self.count=0
        self.start_time = datetime.datetime.now()


    def __call__(self, data):
        self.count+=1
        if self.count%10000==0:

            end = datetime.datetime.now()
            s = (end - self.start_time).total_seconds()
            speed_now = self.count / s
            print(f"speed now {speed_now}")

            self.count = 0
            self.start_time = datetime.datetime.now()


        return data


Pipe(
    range(100000000000),
    SpeedTest(),


)

BotFlow.run()