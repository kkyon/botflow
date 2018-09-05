from botflow import Pipe, Fork,Timer,Branch
from botflow.botframe import BotFrame
from botflow.node import Node
import time


#it will block whole main thread

@Node.boost
def very_slow(a):
    print('i am going to sleep')
    time.sleep(10)
    print('i am aweek')



def main():


    Pipe(
        Timer(delay=1,max_time=10),
        Branch(very_slow),
        print,

    )

    BotFrame.run()


main()
