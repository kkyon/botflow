from databot.flow import Pipe, Loop, Fork,BlockedJoin
from databot.botframe import BotFrame



def double(i):
    return i*2

def triple(i):
    return i*3


def main():
    Pipe(

        range(10),
        BlockedJoin(double,triple),
        print

    )

    BotFrame.render('ex_output/blockedjoin')
    BotFrame.run()



main()
