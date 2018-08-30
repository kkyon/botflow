from databot.flow import Pipe, Branch, Loop
from databot.botframe import BotFrame
from bs4 import BeautifulSoup
from databot.http.http import HttpLoader
from databot.db.aiofile import aiofile
import logging
logging.basicConfig(level=logging.DEBUG)



#定义解析结构
class ResultItem:

    def __init__(self):
        self.id: str = ''
        self.name: str = ''
        self.url: str = ' '
        self.page_rank: int = 0
        self.page_no: int = 0

    def __repr__(self):
        return  '%s,%s,%d,%d'%(str(self.id),self.name,self.page_no,self.page_rank)


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


# 解析分页链接
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


def main():
    words = ['贸易战', '世界杯']
    baidu_url = 'https://www.baidu.com/s?wd=%s'
    urls = [baidu_url % (word) for word in words]




    outputfile=aiofile('ex_output/baidu.txt')
    Pipe(
        urls,
        HttpLoader(),
        Branch(get_all_items,outputfile),
        Branch(get_all_page_url, HttpLoader(), get_all_items, outputfile),

    )
    #生成流程图
    BotFrame.render('ex_output/baiduspider')
    BotFrame.run()


main()





