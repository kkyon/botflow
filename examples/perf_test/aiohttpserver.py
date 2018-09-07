from botflow import *
from aiohttp import web



p = Pipe(

    {"msg":"hello world!"}
)



app = web.Application()

# routes = web.RouteTableDef()
#
# @routes.get('/hello')
# def pipe_json_wrap(p):
#     async def _wrap(request):
#         r=await p(request)
#         return web.json_response(r)
#
#     return _wrap
#
#

app.add_routes([
    web.get('/', p.aiohttp_json_handle())
])


BotFlow.run_app(app)

