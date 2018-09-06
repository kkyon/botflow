from botflow import Pipe, Loop, Fork
from botflow.botframe import BotFrame
from botflow.config import config
import time

def double(a):
    print('double %d'%a)
    time.sleep(1)
    return 2*a
count=0
def triple(a):
    global  count
    count+=1
    if count>6:
        raise Exception()
        pass
    return 3*a

#
config.replay_mode=True

def main():
    Pipe(

        Loop(range(10)),
        double,
        triple,
        print


    )

    BotFrame.run()



main()
