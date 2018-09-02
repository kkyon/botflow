
from aiohttp import ClientSession
import aiohttp
import asyncio
from functools import partial
from databot.node import Node,CountRef
from databot.flow import Route
import json
from aiohttp import web
from databot.botframe import BotFrame
import random
from databot import queue
from databot.bdata import Bdata,BdataFrame
headers = {

    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",

    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    'cache-control': "no-cache",

    }

class HttpRequest(object):

    def __init__(self,url=None,headers=headers,payload=None,method='get'):
        self.url=url

        self.query={}
        self.headers=headers
        self.payload=payload
        self.method=method #GET or POST
        self.cookies=None

    def __setitem__(self, key, value):
        setattr(self,key,value)


    def __getitem__(self, key):
        return getattr(self,key)


    def __repr__(self):

        return "url:{},method:{},payload:{}".format(self.url,self.method,self.payload)

#session tree
class HttpResponse(object):

    def __init__(self,body,encoding):
        self.url=''
        self._body=body
        self._headers=Node
        self._encoding=encoding
        self._cookies = Node
        self._status=Node

    @property
    def text(self,encoding=None,errors='strict'):


        if encoding is None:
            encoding = self._encoding

        return self._body.decode(encoding, errors=errors)

    @property
    def json(self,encoding=None):


        if encoding is None:
            encoding = self._encoding

        return json.loads(self._body.decode(encoding))

    def __repr__(self):
        return 'httpresponse %s'%(id(self))

class HttpLoader(Node):

    def __init__(self,delay=0,proxy=None,header=None,session_policy=None,timeout=20):
        self.delay=delay
        self.timeout=timeout
        super().__init__()

    async def init(self):

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = ClientSession(headers=headers,timeout=timeout, connector=aiohttp.TCPConnector(verify_ssl=False))


    async def close(self):

        await self.session.close()


    async def __call__(self, v):


        if  isinstance(v, str):
            req=HttpRequest()
            req.url=v
            req.method='GET'

        elif isinstance(v,dict):
            req = HttpRequest()
            for k in dir(req):
                if k in v:
                    req[k]=v[k]

        else:

            req=v




        if self.delay==0:
            await asyncio.sleep(random.choice([0,0.1,0.2]))
        else:
            await asyncio.sleep(self.delay)

        to_call=getattr(self.session,req.method.lower())
        response = await  to_call(req.url,headers=req.headers,data=req.payload)




        html = await    response.read()

        resp= HttpResponse(html,response.get_encoding())
        resp.url=response.url
        return resp


class HttpSender(object):
    pass
    #TODO





class HttpServer(Route):


    def __init__(self,route_path="/",port=8080,bind_address='127.0.0.1',timeout=None):


        super().__init__()
        self.route_path=route_path
        self.port=port
        self.bind_address=bind_address
        self.timeout=timeout

    async def response_stream(self, request: web.Request):
        breq = HttpRequest()
        breq.headers = request.headers
        breq.cookies = request.cookies
        breq.url = request.url
        breq.path = request.path
        if breq.path != self.route_path:
            return web.Response(text="error path")
        breq.method = request.method
        breq.payload = await request.text()
        breq.query = request.query


        bdata = Bdata(breq,queue.DataQueue())

        resp = web.StreamResponse(status=200,
                                  reason='OK',
                                  headers={'Content-Type': 'text/html'})

        await resp.prepare(request)

        await self.output_q.put(bdata)
        while True:
            try:
                r:Bdata= await asyncio.wait_for(bdata.ori.get(),10)
                if r.is_BotControl():
                    break
                import json
                json=json.dumps(r.data)
                await resp.write(bytes(json,encoding='utf-8'))
            except Exception as e:
                print(e)

                break

        await resp.write_eof(b'\nend\n')
            #await resp.write(b"heelo")
            #await asyncio.sleep(1)

        return resp

    async def put_input_queue(self,request:web.Request):
        breq=HttpRequest()
        breq.headers=request.headers
        breq.cookies=request.cookies
        breq.url=request.url
        breq.path=request.path
        if breq.path != self.route_path:
            return web.Response(text="error path")
        breq.method=request.method
        breq.payload=await request.text()
        breq.query=request.query
        future = self._loop.create_future()
        bdata=Bdata(breq,breq)

        await self.output_q.put(bdata)

        try:
            r=await asyncio.wait_for(BdataFrame.wait(breq),5)
            BdataFrame.drop_ori(breq)
            return web.json_response(r)
        except:
            BdataFrame.drop_ori(breq)
            raise



    def make_route_bot(self,oq):
        self.share=False
        self.joined=True
        self._loop=asyncio.get_event_loop()

        self.start_q=[queue.NullQueue()]
        self.output_q=oq
        server = web.Server(self.put_input_queue)

        fs=self._loop.create_server(server, self.bind_address, self.port)



        BotFrame.make_bot_raw(self.start_q,self.output_q,fs)

class HttpAck(Route):

    def init_param(self):
        self.window_time=None
        self.window_size=1
        self.window_policy=0.1
        self.buffer={}
        self.raw_bdata = True


    def make_route_bot(self,oq):
        self.init_param()
        self.output_q=oq
        self.start_q=[oq]

    async def route_in(self,bdata):

        import copy
        BdataFrame.set_ack(bdata)
        cp_bdata=  Bdata(bdata.data,ori=0)
        await self.output_q.put(cp_bdata)











