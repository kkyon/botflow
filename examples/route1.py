
from databot.flow import Pipe,Loop,Bypass,Branch,Join
from databot.botframe import BotFrame


class A:
    pass

class B:
    pass


def process_A(i):
    if not isinstance(i,A):
        raise Exception('exception NOT A')
    else:
        print('got class A')

def process_B(i):
    if not isinstance(i,B):
        raise Exception('exception NOT B')
    else:
        print('got class B')

def main():

    Pipe(
            Loop([A(),B(),A(),A(),B()]),
            Branch(process_A,share=False,route_type=A),
            process_B
        )
    BotFrame.run()

    Pipe(
            Loop([A(),B(),A(),A(),B()]),
            Bypass(process_A,route_type=A),
            process_B,
            print
        )
    BotFrame.run()


main()




