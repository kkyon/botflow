from botflow import *
from botflow.node import Flat
from botflow.route import SendTo
from botflow.queue import QueueManager
from botflow.bdata import Databoard
from botflow.config import config
config.queue_max_size=0

QueueManager().debug = True

import datetime

start = datetime.datetime.now()

seen = set()
to_do = set()

count = 1
config.coroutine_batch_size = 16


def fitler(url):
    global count
    if 'http' not in url:
        url = "http://127.0.0.1:8080{}".format(url)

    if url in seen :
        return None

    count += 1

    if count % 10000 == 0:
        print(count)

    seen.add(url)
    return url


def perf_parse(r):
    for a in r.soup.find_all('a', href=True):
        yield a.get('href')


# 0:00:46.989379 是否拆分，区别不大
b = Return(

    fitler,
    HttpLoader(),
    lambda r: r.soup.find_all('a', href=True),
    Flat(),
    lambda r: r.get('href'),


)

# 0:00:45.922213 without boot
# 0:00:43.879830 with boost
c = Return(
    fitler,
    HttpLoader(),
    perf_parse

)

Pipe(
    "http://127.0.0.1:8080/",
    b,
    SendTo(b),

)
BotFlow.render('ex_output/crawler')

try:
    # from pympler.tracker import SummaryTracker
    #
    # tracker = SummaryTracker()
    BotFlow.debug_print()
    BotFlow.run()

except KeyboardInterrupt:

    BotFlow.debug_print()

except:
    raise
end = datetime.datetime.now()
print(end - start)
print(count)
BotFlow.stop()