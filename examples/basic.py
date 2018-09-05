
from botflow.botbase import BotManager
from botflow.node import Flat
from botflow.route import Return,Pipe,Loop,Branch
from botflow import BotFlow

def plus_one(i):
    print(i)
    return i+1


b=Return(
    plus_one,


)





Pipe(
    10,

        Branch(print)






)
BotFlow.render('ex_output/crawler')
try:
    BotFlow.run()
except:
    BotFlow.debug_print()