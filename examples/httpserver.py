from botflow import  *
from botflow import config
from botflow.ex.http import HttpServer
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.DEBUG)
def parse_search(response):
    soup = BeautifulSoup(response.text, "lxml")
    items = soup.find_all('a', href=True)
    result = []
    for rank, item in enumerate(items):
        if len(item['href'])>10 and 'http' in item['href']:
            r={'title':item.get_text(),'href':item['href']}
            yield r


config.exception_policy=config.Exception_ignore

hs=HttpServer()


Pipe(
    hs,
    Join(
    lambda r:"https://www.bing.com/search?q={}".format(r.query['q']),
    lambda r:"https://www.google.com/search?q={}".format(r.query['q']),
    lambda r:"https://www.baidu.com/s?wd={}".format(r.query['q']),
    ),

    Branch(print), #for debug ,show url

    HttpLoader(timeout=3),
    parse_search,


    Zip(n_stream=3),
    Branch(print),
    SendTo(hs),
    print,


)

# Pipe('https://www.bing.com/search?q=kkyon',
#      HttpLoader(),
#      parse_google,
#      print)
BotFlow.render('ex_output/httpserver')
BotFlow.run()