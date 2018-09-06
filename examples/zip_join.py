from botflow import Pipe,Join
from botflow.node import Zip
from botflow import BotFlow



def double(i):
    return i*2

def triple(i):
    return i*3

def plus_one(i):
    return i+1

def print_out(m:list):
    print(m)

def main():
    Pipe(

        range(10),
        Join(
                    double,
                    triple
        ),
            plus_one,
            plus_one,


        Zip(n_stream=2),
        print_out,

    )

    BotFlow.render('ex_output/blockedjoin')
    BotFlow.run()



main()
