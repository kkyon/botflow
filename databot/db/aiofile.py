from databot.node import Node
from functools import partial
import asyncio

class aiofile(Node):

    async def open(self,filename,mode='w'):


        cb = partial(open, filename, mode=mode, encoding="utf-8")
        fd=await  self.loop.run_in_executor(None, cb)
        return fd

    def __init__(self,fileame,mode='w'):
        self.filename=fileame
        self.mode=mode
        self.fd=None
        self.loop=asyncio.get_event_loop()
        super().__init__()

    async def init(self):
        self.fd = await self.open(self.filename, self.mode)
    async def close(self):
        await  self.loop.run_in_executor(None, self.fd.close)

    async def __call__(self, text):
        if not isinstance(text,(str,bytes)):
            text=text.__repr__()
        text+="\n"
        await  self.loop.run_in_executor(None, self.fd.write,text)