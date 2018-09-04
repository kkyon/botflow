from databot import *
from databot.node import Flat
from databot.route import SendTo
from databot.queue import QueueManager
from databot.bdata import Databoard
QueueManager().debug=True
Databoard().debug=True

seen=set()
count=1
def fitler(url):
    if url in seen:
        return None

    seen.add(url)
    if 'http' not in url:
        url="http://127.0.0.1:8080{}".format(url)

    return url
def incr_count(url):
    global count

    if url not in seen:
        count += 1
        if count%100 ==0:
            print(count)
        return url


b=Return(
    fitler,
    HttpLoader(),
    lambda r: r.soup.find_all('a', href=True),
    Flat(),
    lambda r: r.get('href'),
    fitler,
    incr_count,



)



Pipe(
    "http://127.0.0.1:8080/",
    b,
    SendTo(b),
    Branch(print),



)
Bot.render('ex_output/crawler')


try:
    # from pympler.tracker import SummaryTracker
    #
    # tracker = SummaryTracker()

    Bot.run()
except KeyboardInterrupt:

    Bot.debug_print()

except:
    raise