from botflow import *
from pympler import tracker
import logging

logging.basicConfig(level=logging.DEBUG)

count=0
def check_and_count(i):
    global count
    count+=1
    if count>9900:
        raise Exception()


Pipe(
    HttpServer(),
    {'message': 'Hello, World!'},

    HttpAck(),


)
try:
    from pympler.tracker import SummaryTracker

    tracker = SummaryTracker()
    BotFlow.run()
except:
    tracker.print_diff()
    raise