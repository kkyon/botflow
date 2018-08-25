
from aiohttp import ClientSession
import aiohttp
import asyncio
from functools import partial
from databot.node import Node
import json
import random
headers = {

    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",

    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    'cache-control': "no-cache",
    'postman-token': "a2e4dba4-0193-451c-fb7c-40766421ef1f"
    }
#session tree
class HttpResponse(object):

    def __init__(self,body,encoding):
        self._body=body
        self._encoding=encoding

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


    async def __call__(self, url):

        if not isinstance(url, str):
            url = url.url
        if self.delay==0:
            await asyncio.sleep(random.choice([0,0.1,0.2]))
        else:
            await asyncio.sleep(self.delay)
        response = await self.session.get(url, headers=headers)
        html = await    response.read()

        return HttpResponse(html,response.get_encoding())


class HttpSender(object):
    pass
    #TODO




