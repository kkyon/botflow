from botflow import *
from aiohttp import web



p = Pipe(

    {"msg":"hello world!"}
)



app = web.Application()

app.add_routes([
    web.get('/', p.aiohttp_json_handle)
])


BotFlow.run_app(app)
#BotFlow start web server http://0.0.0.0:8080

