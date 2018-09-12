
from botflow import Pipe, Branch,Join,Filter,Timer
from botflow import BotFlow

class A:
    pass
class B:
    pass

class C:
    pass


class Counter:
    def __init__(self,name='counter'):
        self.count=0
        self.name=name
    def __call__(self, data):
        self.count=self.count+1
        return data


    a_count=0
    b_count = 0
    c_count = 0
def only_a(i):

    assert(isinstance(i, A))
    return i

def only_b(i):

    assert(isinstance(i, B))
    return i

def only_c(i):

    assert(isinstance(i, C))
    return i


def a_to_b(i):
    return B()

#
def test_routetype():
    BotFlow.reset()
    Pipe(
        [A(),B(),A()],
        Branch(only_a,route_type=A)
    )
    BotFlow.run()
#
def test_routetype_no_shared():
    BotFlow.reset()
    Pipe(
        [A(),B(),A()],
        Branch(only_a,route_type=A,share=False),
        only_b
    )
    BotFlow.run()
#
def test_routetype_count():
    BotFlow.reset()
    b_counter=Counter()
    a_counter=Counter()
    Pipe(
        [A(),B(),A()],
        Branch(only_a,a_counter,a_to_b,route_type=A,share=False,join=True),
        only_b,
        b_counter
    )
    BotFlow.run()
    assert(b_counter.count==3)
    assert(a_counter.count == 2)

#
#
def test_routetype_count2():
    BotFlow.reset()
    b_counter=Counter()
    b1_counter = Counter()
    counter=Counter('count2')
    counter1 = Counter('count1')
    p=Pipe(
        [A(),B(),A()],
        Branch(only_b,counter1,route_type=B, join=True,share=True),
        counter,
        Branch(only_a,a_to_b,only_b,b1_counter,route_type=A,share=False,join=True),
        only_b,
        b_counter
    )

    BotFlow.run()
    assert (counter1.count == 1)
    assert (counter.count ==  4)

    assert (b1_counter.count == 2)
    assert (b_counter.count == 4)


def test_routetype_count3():
    BotFlow.reset()
    a_counter=Counter()
    b_counter=Counter()
    c_counter=Counter()

    p = Pipe(
        [A(), B(), A(),C(),C()],

        Branch(lambda i:isinstance(i,(A,C)),
               route_type=[A,C]),

        Branch(
                Branch( only_c,c_counter,route_type=C),

               share=False,
               route_type=[A, C]),

    )

    BotFlow.run()
    assert (c_counter.count == 2)

# def test_fork():
#     BotFlow.reset()
#     a_count=0
#     b_count = 0
#     p=Pipe(
#         [A(),A()],
#         Fork(a_to_b,a_to_b,share=False,join=True),
#         only_b
#
#     )
#
#     BotFlow.run()

def test_double_loop():
    BotFlow.reset()
    count=0
    def sum(x):
        nonlocal count
        count+=x


    p = Pipe(
        range(10),
        range(10),
        sum


    )

    BotFlow.run()
    assert count==45*10




def test_filter():
    BotFlow.reset()
    Pipe(
        [A(),B(),C()],
        Filter(filter_types=A),
        only_a

    )
    BotFlow.run()
#
def test_filter2():

    BotFlow.reset()
    Pipe(
        [A(),B(),C()],
        Filter(filter_func=lambda r:isinstance(r,A)),
        only_a

    )
    BotFlow.run()
#
def test_filter3():
    BotFlow.reset()
    Pipe(

        [A(),B(),C()],
        Filter(filter_types=[A,B],filter_func=lambda r:isinstance(r,(A,C))),
        only_a

    )

    BotFlow.run()


