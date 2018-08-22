from databot.flow import Pipe, Branch, Loop
from databot.botframe import BotFrame
from bs4 import BeautifulSoup
from dataclasses import dataclass
from databot.http.http import HttpLoader


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
def get_all_items(html):
    soup = BeautifulSoup(html, "lxml")
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
def get_all_page_url(html):
    itemList = []
    soup = BeautifulSoup(html, "lxml")
    page = soup.select('div#page')
    for item in page[0].find_all('a'):
        href = item.get('href')
        no = item.get_text()
        if '下一页' in no:
            break
        itemList.append('https://www.baidu.com' + href)

    return itemList


def main():
    words = ['贸易战', '世界杯']
    baidu_url = 'https://www.baidu.com/s?wd=%s'
    urls = [baidu_url % (word) for word in words]

    # make data flow net
    Pipe(
        Loop(urls),
        HttpLoader(),
        Branch(get_all_items, print),
        Branch(get_all_page_url, HttpLoader(), get_all_items, print),

    )
    BotFrame.run()


main()



