===========================
Databot
===========================

*data driven programming framework with asyncio.
*it hided complex async programming detail .every processor unit will act like a bot .
*The framework also provider type and content base route function.


Installing
----------

Install and update using `pip`_:


    pip install -U databot


A Simple Example
----------------

.. code-block:: python


    from databot.flow import Pipe, Loop, Fork
    from databot.botframe import BotFrame


    class Sum(object):

        def __init__(self):
            self.sum = 0

        def __call__(self, i):
            self.sum += i
            return self.sum

        def __repr__(self):
            return 'sum:' + str(self.sum)


    op_sum = Sum()


    def main():
        Pipe(

            Loop(range(1000000)),
            Fork(op_sum),
            print

        )

        BotFrame.run()
        print(op_sum)


    main()


A Spider(crawler) Example
----------------
.. code-block:: python


    from databot.flow import Pipe, Branch, Loop,Join,Timer
    from databot.botframe import BotFrame
    from bs4 import BeautifulSoup
    from databot.http.http import HttpLoader,HttpResponse
    from databot.db.mysql import Insert
    from databot.db.aiofile import aiofile
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
            return  '%s,%s,%d,%d'%(str(self.id),self.name,self.page_no,self.page_rank)



    class UrlItem:
        def __init__(self):
            self.name: str=''
            self.url: str=''


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

    def show_info(i):
        BotFrame.debug()

    def main():
        words = ['贸易战', '世界杯']
        baidu_url = 'https://www.baidu.com/s?wd=%s'
        urls = [baidu_url % (word) for word in words]


        outputfile=aiofile('baidu.txt')
        Pipe(
            Loop(urls),
            HttpLoader(),
            Branch(get_all_items,outputfile),
            Branch(get_all_page_url, HttpLoader(), get_all_items, outputfile),

        )

        BotFrame.run()


    main()



.. code-block:: text

   * it will scraped 20 pages and 191 items with in 5s . it has very high performance .
   * 5秒钟可以完成，20个网页，包含191个条目抓取。 根据外部资料asyncio 1分钟可以完成，1百万个网页抓取。databot可以达到相近性能。


Contributing
------------




Donate
------




Links
-----