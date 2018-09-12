
from botflow import Return,Pipe,Branch,Join
from botflow import BotFlow,Filter
import logging
logging.basicConfig(level=logging.DEBUG)
logger=logging.getLogger('botflow.bot')
logger.setLevel(logging.DEBUG)
logger=logging.getLogger('botflow.pipe')
logger.setLevel(logging.DEBUG)

p=Pipe(
        ["a","b","c"],
)

p1=Pipe(lambda x:x+2)

p3=Pipe(lambda x:x+10,
        Branch(p,print),
    p1)



# BotFrame.make_pipe([p1])
# BotFlow.debug_print()
#
#print(p3(1))
BotFlow.render("ex_output/basic")
BotFlow.run(p3,p)
