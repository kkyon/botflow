
from botflow.botbase import BotManager
from botflow.node import Flat
from botflow.route import Return,Pipe,Loop,Branch,Join
from botflow import BotFlow,Filter
from botflow.node import Delay,Zip
from botflow.config import config

class A:
    pass
class B:
    pass

class C:
    pass

def only_a(data):
    if not isinstance(data,A):
        raise Exception()

def check_stop(i):
    if i>10:
        BotFlow.stop()

    return i

Pipe(
    Join(
        "a","b","c"

    ),
    Zip(n_stream=3),
    lambda r:'l_'+r,
    print,


)


BotFlow.render("ex_output/test")
BotFlow.run()

