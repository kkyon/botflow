
from aiohttp import ClientSession
import aiohttp
import asyncio
from functools import partial
from databot.node import Node,CountRef
import json
import random
headers = {

    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",

    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    'cache-control': "no-cache",
    'postman-token': "a2e4dba4-0193-451c-fb7c-40766421ef1f"
    }

class HttpRequest(object):

    def __init__(self,url=None,headers=headers,payload=None,method='get'):
        self.url=url
        self.headers=headers
        self.payload=payload
        self.method=method #GET or POST
        self.cookies=None

    def __setitem__(self, key, value):
        setattr(self,key,value)


    def __getitem__(self, key):
        return getattr(self,key)

#session tree
class HttpResponse(object):

    def __init__(self,body,encoding):
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

        return HttpResponse(html,response.get_encoding())


class HttpSender(object):
    pass
    #TODO




