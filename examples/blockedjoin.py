from botflow import Pipe,Join
from botflow.node import Zip
from botflow.botframe import BotFrame



def double(i):
    return i*2

def triple(i):
    return i*3

def plus_one(i):
    return i+1

def print_out(m):
    print(m)

def main():
    Pipe(

        range(100),
        Join(
                    double,
                    triple),
            plus_one,
            plus_one,


        Zip(n_stream=2),
        print_out

    )

    BotFrame.render('ex_output/blockedjoin')
    BotFrame.run()



main()
