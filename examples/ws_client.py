import aiohttp
import asyncio

async def main():
    session = aiohttp.ClientSession()
    ws = await session.ws_connect(
        'http://127.0.0.1:8080/ws')

    while True:
        msg = await ws.receive()

        if msg.tp == aiohttp.MsgType.text:
            if msg.data == 'close':
               await ws.close()
               break
            else:
               ws.send_str(msg.data + '/answer')
        elif msg.tp == aiohttp.MsgType.closed:
            break
        elif msg.tp == aiohttp.MsgType.error:
            break




loop = asyncio.get_event_loop()



loop.run_until_complete(main())