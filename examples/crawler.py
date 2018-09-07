import logging


#logging.basicConfig(level=logging.DEBUG)
logger=logging.getLogger(__name__)
from botflow import *
from botflow.route import SendTo
from botflow.config import config
from botflow.node import Delay,Node,SpeedLimit
from botflow.queue import QueueManager
config.coroutine_batch_size = 8
config.default_queue_max_size=0


import datetime

start = datetime.datetime.now()

seen = set()
to_do = set()

count = 1

def print_speed():
    end = datetime.datetime.now()
    s=(end-start).total_seconds()
    print(f"count {count} time {s} speed{count/s}")
    # QueueManager().debug_print()

def fitler(url):
    global count
    if 'http' not in url:
        url = "http://127.0.0.1:8080{}".format(url)

    if url in seen :
        return None

    count += 1

    if count % 5000 == 0:
        print_speed()

    seen.add(url)
    return url


def perf_parse(r):
    for a in r.soup.find_all('a', href=True):
        yield a.get('href')




# 0:00:46.989379 是否拆分，区别不大
b = Return(

    fitler,
    HttpLoader(),
    perf_parse,




)


Pipe(
    "http://127.0.0.1:8080/",
    b,
    SendTo(b),

)
BotFlow.render('ex_output/crawler')

try:

    BotFlow.debug_print()
    BotFlow.run()

except KeyboardInterrupt:

    BotFlow.debug_print()

except:
    raise
BotFlow.debug_print()
print_speed()
BotFlow.stop()