from databot.flow import Pipe, Loop, Fork,BlockedJoin,Merge,Join
from databot.botframe import BotFrame



def double(i):
    return i*2

def triple(i):
    return i*3

def plus_one(i):
    return i+1

merge=Merge()
def main():
    Pipe(

        range(100),
        Join(
                    double,
                    triple,merge_node=merge),
            plus_one,
            plus_one,
        merge,
        print

    )

    BotFrame.render('ex_output/blockedjoin')
    BotFrame.run()



main()
