import logging
from botflow import *
from botflow.route import Link
from botflow.config import config
import datetime



config.default_queue_max_size = 0
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


start = datetime.datetime.now()

seen = set()

count = 1


def print_speed():
    end = datetime.datetime.now()
    s = (end - start).total_seconds()
    print(f"count {count} time {s} speed{count/s}")
    # QueueManager().debug_print()


def filter_out(url):
    global count
    if 'http' not in url:
        url = "http://127.0.0.1:8080{}".format(url)

    if url in seen:
        return None

    count += 1

    if count % 5000 == 0:
        print_speed()

    seen.add(url)
    return url


def find_all_links(r):
    for a in r.soup.find_all('a', href=True):
        yield a.get('href')


b = Pipe(

    filter_out,
    HttpLoader(),
    find_all_links,
)

Pipe(
    "http://127.0.0.1:8080/",
    b,
    Link(b),

)
Bot.render('ex_output/crawler')

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
