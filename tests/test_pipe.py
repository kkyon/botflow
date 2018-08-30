from unittest import TestCase
from databot.flow import Pipe, Branch, Loop,Join,Fork,Filter,Timer
from databot.botframe import BotFrame

class A:
    pass
class B:
    pass

class C:
    pass




def only_b(self,i):
        self.b_count += 1
        self.assertTrue(isinstance(i, B))
        return i


class TestPipe(TestCase):
    a_count=0
    b_count = 0
    c_count = 0
    def only_a(self,i):
        self.a_count+=1
        self.assertTrue(isinstance(i, A))
        return i

    def only_b(self,i):
        self.b_count += 1
        self.assertTrue(isinstance(i, B))
        return i

    def only_c(self,i):
        self.c_count += 1
        self.assertTrue(isinstance(i, C))
        return i


    def a_to_b(self,i):
        return B()


    def test_routetype(self):
        Pipe(
            Loop([A(),B(),A()]),
            Branch(self.only_a,route_type=A)
        )
        BotFrame.run()

    def test_routetype_no_shared(self):
        Pipe(
            Loop([A(),B(),A()]),
            Branch(self.only_a,route_type=A,share=False),
            self.only_b
        )
        BotFrame.run()

    def test_routetype_count(self):
        self.a_count=0
        self.b_count = 0
        Pipe(
            Loop([A(),B(),A()]),
            Branch(self.only_a,self.a_to_b,route_type=A,share=False,join=True),
            self.only_b
        )
        BotFrame.run()
        self.assertTrue(self.b_count==3)
        self.assertTrue(self.a_count == 2)



    def test_routetype_count2(self):
        self.a_count=0
        self.b_count = 0
        p=Pipe(
            Loop([A(),B(),A()]),
            Branch(self.only_b, route_type=B, join=True),
            Branch(self.only_a,self.a_to_b,route_type=A,share=False,join=True),
            self.only_b
        )
        self.assertFalse(p.finished())
        BotFrame.run()
        self.assertEqual(self.b_count,5)
        self.assertEqual(self.a_count, 2)
        self.assertTrue(p.finished())

    def test_routetype_count3(self):
        self.a_count = 0
        self.b_count = 0
        self.c_count = 0
        p = Pipe(
            [A(), B(), A(),C(),C()],

            Branch(lambda i:isinstance(i,(A,C)),self.assertTrue,
                   route_type=[A,C]),

            Branch(
                    Branch( self.only_c,route_type=C),

                   share=False,
                   route_type=[A, C]),

        )

        BotFrame.run()
        self.assertEqual(self.c_count,2)

    def test_fork(self):
        self.a_count=0
        self.b_count = 0
        p=Pipe(
            Loop([A(),A()]),
            Fork(self.a_to_b,self.a_to_b,share=False,join=True),
            self.only_b

        )

        BotFrame.run()

    def test_double_loop(self):

        count=0
        def sum(x):
            nonlocal count
            count+=x


        p = Pipe(
            Loop(range(10)),
            Loop(range(10)),
            sum


        )

        BotFrame.run()
        self.assertEqual(count,45*10)

    def test_double_loop(self):

        count=0
        def sum(x):
            nonlocal count
            count+=x


        p = Pipe(
            Loop(range(10)),
            Loop(range(10)),
            sum


        )

        BotFrame.run()
        self.assertEqual(count,45*10)

    def test_loop_double(self):
        count = 0

        def sum(x):
            nonlocal count
            count += x

        p = Pipe(
            Loop(range(10)),
            Loop(range(10)),
            sum

        )

        BotFrame.run()
        self.assertEqual(count, 45 * 10)


    def test_blockedjoin(self):

        from databot.flow import BlockedJoin
        def check(r):
            self.assertEqual(len(r),2)
            self.assertTrue(isinstance(r[0],B))
            self.assertTrue(isinstance(r[0],B))

        p = Pipe(
            Loop([A()]),
            BlockedJoin(self.a_to_b,
                        self.a_to_b

                        ),

            check
        )

        BotFrame.run()

    def test_blockedjoin_exception2(self):

        from databot.flow import BlockedJoin

        from databot.config import config
        config.exception_policy=config.Exception_pipein


        def raise_exception(a):
            raise Exception()
        def check(r):
            self.assertEqual(len(r),2)
            self.assertTrue(isinstance(r[0],Exception))
            self.assertTrue(isinstance(r[1],B))

        p = Pipe(
            Loop([A()]),
            BlockedJoin(raise_exception,
                        self.a_to_b

                        ),

            check
        )

        BotFrame.run()
        config.exception_policy = config.Exception_default

    def test_filter(self):

        Pipe(
            [A(),B(),C()],
            Filter(route_type=A),
            self.only_a

        )
        BotFrame.run()

    def test_filter2(self):

        Pipe(
            [A(),B(),C()],
            Filter(route_func=lambda r:isinstance(r,A)),
            self.only_a

        )
        BotFrame.run()

    def test_filter3(self):

        Pipe(

            [A(),B(),C()],
            Filter(route_type=[A,B],route_func=lambda r:isinstance(r,(A,C))),
            self.only_a

        )

        BotFrame.run()

    # def test_boost(self):
    #     import time
    #
    #
    #     def very_slow(a):
    #         time.sleep(10)
    #
    #
    #     Pipe(
    #         Timer(delay=1),
    #         Branch(very_slow),
    #         print,
    #
    #
    #     )
    #     BotFrame.run()

