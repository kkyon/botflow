from databot.flow import Pipe, Loop, Fork
from databot.botframe import BotFrame
from databot.config import config


def step_test(a):
    print(a)
    return a
count=0
def exception(a):
    global  count
    count+=1

#
config.palyback_mode=True

def main():
    Pipe(

        Loop(range(100)),
        step_test,
        exception


    )

    BotFrame.run()



main()
