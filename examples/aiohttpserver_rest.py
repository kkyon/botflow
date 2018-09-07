from botflow import  *
from botflow import config
from bs4 import BeautifulSoup
from aiohttp import web
import aiohttp
import logging

logging.basicConfig(level=logging.DEBUG)

config.exception_policy=config.Exception_ignore

def parse_search(response):
    # raise Exception()
    soup = BeautifulSoup(response.text, "lxml")
    items = soup.find_all('a', href=True)
    result = []
    for rank, item in enumerate(items):
        if len(item.get_text())>10 and 'http' in item['href']:
            r={'title':item.get_text(),'href':item['href']}
            result.append(r)
    return result


p=Pipe(

    lambda r:r.query['q'],
    Join(
    lambda q:"https://www.bing.com/search?q={}".format(q),
    lambda q:"https://www.google.com/search?q={}".format(q),
    lambda q:"https://www.baidu.com/s?wd={}".format(q),
    ),

    Zip(n_stream=3),
    HttpLoader(),
    parse_search,
)

routes = web.RouteTableDef()
@routes.get('/')
async def json_handle(request):
    r = await p(request)
    return web.json_response(r)





app = web.Application()
#app.add_routes([web.get('/', json_handle)])
app.add_routes(routes)


BotFlow.render('ex_output/httpserver')
BotFlow.run_app(app)

