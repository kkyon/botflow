import asyncio
import aiomysql

loop = asyncio.get_event_loop()

def f():
    pass
async def d():
    return 'ddd'

async def e():

    r=await d()
    return r

async def g():
    yield 'gg'


async def example():
    r=await e()
    print(r)


loop.run_until_complete(example())