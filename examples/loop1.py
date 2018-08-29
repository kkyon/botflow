from databot.flow import Pipe, Fork
from databot.botframe import BotFrame


class Sum(object):

    def __init__(self):
        self.sum = 0

    def __call__(self, i):
        self.sum += i
        return self.sum

    def __repr__(self):
        return 'sum:' + str(self.sum)


op_sum = Sum()


def main():
    Pipe(

        range(1000000),
        Fork(op_sum),
        print

    )

    BotFrame.run()
    print(op_sum)


main()
