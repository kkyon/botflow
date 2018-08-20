
from databot.flow import Pipe,Loop,Bypass
from databot.bot import Bot


class Sum(object):

    def __init__(self):
        self.sum=0

    def __call__(self, i):
        self.sum+=i

    def __repr__(self):
        return 'sum:'+str(self.sum)

op_sum=Sum()

def main():




    Pipe(

            Loop(range(10)),
            Bypass(print, op_sum),

        )


    Bot.run()
    print(op_sum)




main()




