
from botflow import Pipe, Branch, Loop,Join,Fork,Filter,Timer
from botflow import BotFlow
from botflow.node import Delay
class A:
    pass
class B:
    pass

class C:
    pass


def test_stop():
    def check_stop(i):
        if i>10:
            BotFlow.stop()

        return i
    BotFlow.reset()
    Pipe(
        range(10000),
        Delay(),
        check_stop,
        print,


    )
    BotFlow.run()
    assert True