from databot.flow import Pipe, Branch, Loop, Timer
from databot.botframe import BotFrame
from bs4 import BeautifulSoup
from dataclasses import dataclass
from databot.http.http import HttpLoader
from databot.config import config


@dataclass
class ResultItem:
    id: str = ''
    name: str = ''
    url: str = ' '
    page_rank: int = 0
    page_no: int = 0

    def __repr__(self):
        return self.name


@dataclass
class UrlItem:
    name: str
    url: str


# 解析具体条目
def get_all_items(response):
    soup = BeautifulSoup(response.text, "lxml")
    items = soup.select('div.result.c-container')
    result = []
    for rank, item in enumerate(items):
        import uuid
        id = uuid.uuid4()
        r = ResultItem()
        r.id = id
        r.page_rank = rank
        r.name = item.h3.get_text()
        result.append(r)
    return result


# 解析 分页 链接
def get_all_page_url(response):
    itemList = []
    soup = BeautifulSoup(response.text, "lxml")
    page = soup.select('div#page')
    for item in page[0].find_all('a'):
        href = item.get('href')
        no = item.get_text()
        if '下一页' in no:
            break
        itemList.append('https://www.baidu.com' + href)

    return itemList


result = []

delay=5
def collect(i):
    result.append(i)


def show_progress(count):
    n=len(result)
    speed=n/(count*delay)
    print('got len item %s speed:%03f per second,total cost: %ss'%(n,speed,count*delay))



config.exception_policy=config.Exception_ignore
def main():
    words = ['贸易战', '世界杯']*50
    baidu_url = 'https://www.baidu.com/s?wd=%s'
    urls = [baidu_url % (word) for word in words]

    # make data flow net
    p1=Pipe(
        Loop(urls),
        HttpLoader(),
        Branch(get_all_items, collect),
        Branch(get_all_page_url, HttpLoader(), get_all_items, collect),

    )
    Pipe(Timer(delay=delay, until=p1.finished), show_progress)
    BotFrame.run()


main()

#
# ---run result----
#post man test result for a page requrest ;1100ms
#
# PING www.a.shifen.com (180.97.33.108): 56 data bytes
# 64 bytes from 180.97.33.108: icmp_seq=0 ttl=55 time=41.159 ms

# got len item 9274 speed:52.994286 per second,total cost: 175s
# got len item 9543 speed:53.016667 per second,total cost: 180s
# got len item 9614 speed:51.967568 per second,total cost: 185s


#best test data

#25 pages per seconde.
# got len item 1540 speed:102.666667 per second,total cost: 15s
# got len item 2549 speed:127.450000 per second,total cost: 20s
# got len item 3450 speed:138.000000 per second,total cost: 25s
# got len item 4843 speed:161.433333 per second,total cost: 30s
# got len item 6070 speed:173.428571 per second,total cost: 35s
# got len item 6826 speed:170.650000 per second,total cost: 40s
# got len item 7773 speed:172.733333 per second,total cost: 45s
# got len item 8681 speed:173.620000 per second,total cost: 50s
# got len item 9700 speed:176.363636 per second,total cost: 55s






