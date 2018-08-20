
from aiohttp import ClientSession
import aiohttp
import asyncio
from functools import partial
from databot.flow import Node
headers = {

    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    'x-devtools-emulate-network-conditions-client-id': "D7F61FC8C976D389ABC1B009F0567FEA",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    'cache-control': "no-cache",
    'postman-token': "a2e4dba4-0193-451c-fb7c-40766421ef1f"
    }
#session tree

class HttpLoader(Node):

    def __init__(self,speed=None,proxy=None,header=None,session_policy=None):
        self.speed=speed

    async def node_init(self):
        self.session = ClientSession(headers=headers, connector=aiohttp.TCPConnector(verify_ssl=False))


    async def node_close(self):
        await self.session.close()


    async def __call__(self, url):

        if not isinstance(url, str):
            url = url.url
        response = await self.session.get(url, headers=headers)
        html = await    response.read()

        return html


class HttpSender(object):
    pass
    #TODO


class FileSaver(Node):

    async def open(self,filename,mode='a'):


        cb = partial(open, filename, mode=mode)
        fd=await  self.loop.run_in_executor(None, cb)
        return fd

    def __init__(self,fileame,mode='a'):
        self.filename=fileame
        self.mode=mode
        self.fd=None
        self.loop=asyncio.get_event_loop()

    async def node_init(self):
        self.fd = await self.open(self.filename, self.mode)
    async def node_close(self):
        await  self.loop.run_in_executor(None, self.fd.close)

    async def __call__(self, text):




        await  self.loop.run_in_executor(None, self.fd.write,text)


