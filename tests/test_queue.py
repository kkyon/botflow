import asyncio
from botflow.queue import DataQueue ,ConditionalQueue
from botflow.bdata import Bdata

import logging
logger=logging.getLogger("botflow.queue")
logger.setLevel(logging.DEBUG)
sum=0


import asyncio
import aiomysql

loop = asyncio.get_event_loop()







async def fa():
    ori1=Bdata.make_Bdata_zori(1)
    ori2 = Bdata.make_Bdata_zori(2)
    q = ConditionalQueue()
    for i in range(100):
        await q.put(Bdata(4, ori2))
    await q.put(Bdata(3,ori1))


    o1= asyncio.ensure_future(q.get(ori1))

    result=await asyncio.gather(o1)
    assert result[0].data==3




def test_get_by():
    loop.run_until_complete(fa())
