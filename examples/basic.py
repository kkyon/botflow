from databot import *
from databot.botbase import BotManager
from databot.node import Flat


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
Bot.render('ex_output/crawler')

BotManager().debug_print()
Bot.run()