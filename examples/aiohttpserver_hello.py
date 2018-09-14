import logging
logging.basicConfig(level=logging.DEBUG)
from botflow import *

from aiohttp import web



p = Pipe(

    {"msg":"hello world!"}
)



app = web.Application()

app.add_routes([
    web.get('/', p.aiohttp_json_handle)
])


Bot.run_app(app,port=8081)
#BotFlow start web server http://0.0.0.0:8080

