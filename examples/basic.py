
from databot.botbase import BotManager
from databot.node import Flat
from databot.route import Return,Pipe,Loop,Branch
from databot.botframe import BotFlow

def plus_one(i):
    print(i)
    return i+1


b=Return(
    plus_one,


)





Pipe(
    10,
    Loop(
        plus_one,
        Branch(print)
         ),





)
BotFlow.render('ex_output/crawler')
try:
    BotFlow.run()
except:
    BotFlow.debug_print()