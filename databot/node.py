import asyncio




class Node(object):
    async def node_init(self):
        await asyncio.sleep(0)
    async def node_close(self):
        await asyncio.sleep(0)

