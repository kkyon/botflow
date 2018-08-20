===========================
Databot
===========================

*data flow processing framework with asyncio.
*it hided complex async programmoing detail .every processor unit will act like a bot .
*The framework also provider type and content base route function.


Installing
----------

Install and update using `pip`_:

.. code-block:: text

    pip install -U databot


A Simple Example
----------------

.. code-block:: python


    from databot.flow import Pipe,Loop,Bypass
    from databot.bot import Bot


    class Sum(object):

        def __init__(self):
            self.sum=0

        def __call__(self, i):
            self.sum+=i

        def __repr__(self):
            return 'sum:'+str(self.sum)

    op_sum=Sum()

    def main():
        Pipe(

                Loop(range(10)),
                Bypass(print, op_sum),

            )
        Bot.run()
        print(op_sum)




    main()

A Spider(crawler) Example
----------------
.. code-block:: python

    from databot.flow import Pipe,Bypass,Branch,Loop
    from databot.bot import Bot
    from bs4 import BeautifulSoup
    from dataclasses import dataclass
    from databot.httploader import HttpLoader

    @dataclass
    class ResultItem:
        id:str=''
        name: str =''
        url: str =' '
        page_rank:int = 0
        page_no:int =0

        def __repr__(self):
            return self.name



    @dataclass
    class UrlItem:
        name: str
        url: str


    #解析具体条目
    def get_all_items(html):

        soup = BeautifulSoup(html,"lxml")
        items=soup.select('div.result.c-container')
        result=[]
        for rank,item in enumerate(items):
            import uuid
            id=uuid.uuid4()
            r = ResultItem()
            r.id=id
            r.page_rank=rank
            r.name=item.h3.get_text()
            result.append(r)
        return result



    #解析 分页 链接
    def get_all_page_url(html):

        itemList=[]
        soup = BeautifulSoup(html,"lxml")
        page=soup.select('div#page')
        for item in page[0].find_all('a'):
            href=item.get('href')
            no=item.get_text()
            if '下一页' in no:
                break
            itemList.append('https://www.baidu.com'+href)

        return itemList

    def main():
        words = ['贸易战', '世界杯']
        baidu_url = 'https://www.baidu.com/s?wd=%s'
        urls=[baidu_url % (word)  for word in words]

        #make data flow net
        Pipe(
                 Loop(urls),
                 HttpLoader(),
                 Branch(get_all_items,print),
                 Branch(get_all_page_url, HttpLoader(), get_all_items,print),

             )
        Bot.run()

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