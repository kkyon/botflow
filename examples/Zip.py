import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('asyncio').setLevel(logging.DEBUG)
from botflow import *

p1=Pipe(lambda x:x+1)
p2=Pipe(lambda x:x+2)

p=Pipe(

    Zip(p1,p2)


)

print(p.run(range(0,10)))
#BotFlow.render("ex_output/test")
# BotFlow.run()