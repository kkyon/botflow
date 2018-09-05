from databot import Pipe, Branch, Loop,Join,Fork,Timer,BotFlow

from bs4 import BeautifulSoup
from databot.http.http import HttpLoader,HttpResponse
from databot.db.mysql import Insert
import logging
logging.basicConfig(level=logging.DEBUG)


class ResultItem:

    def __init__(self):
        self.id: str = ''
        self.name: str = ''
        self.url: str = ' '
        self.page_rank: int = 0
        self.page_no: int = 0

    def __repr__(self):
        return self.name



class UrlItem:
    def __init__(self):
        self.name: str=''
        self.url: str=''


dbconf={}
dbconf['host']= '127.0.0.1'
dbconf['port']=3306
dbconf['user']= 'root'
dbconf['password']= 'admin123'
dbconf['db']= 'test'


# 解析具体条目
def get_all_items(response):
    soup = BeautifulSoup(response.text, "lxml")
    items = soup.select('div.result.c-container')

    for rank, item in enumerate(items):
        import uuid
        id = uuid.uuid4()
        r = ResultItem()
        r.id = id
        r.page_rank = rank
        r.name = item.h3.get_text()
        yield r



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
        r='https://www.baidu.com' + href
        yield r




def show_info(i):
    BotFlow.debug_print()
def main():
    words = ['贸易战']
    baidu_url = 'https://www.baidu.com/s?wd=%s'
    urls = [baidu_url % (word) for word in words]

    # make data flow net
    insert=Insert("insert into test.baidu (id,name ,url,page_rank,page_no)values('{id}','{name}' ,'{url}',{page_rank},{page_no})",**dbconf)

    p=Pipe(
        urls,
        HttpLoader(),
        Branch(get_all_items,join=True),

        Branch(get_all_page_url, HttpLoader(), get_all_items,share=False,join=True,route_type=HttpResponse),

        insert,
    )

    Pipe(Timer(delay=2), Branch(print),show_info)

    BotFlow.render('ex_output/baiduspider')
    BotFlow.run()

main()



