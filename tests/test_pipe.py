from unittest import TestCase
from databot.flow import Pipe, Branch, Loop,Join,Fork
from databot.botframe import BotFrame

class A:
    pass
class B:
    pass



class TestPipe(TestCase):
    a_count=0
    b_count = 0
    def only_a(self,i):
        self.a_count+=1
        self.assertTrue(isinstance(i, A))
        return i

    def only_b(self,i):
        self.b_count += 1
        self.assertTrue(isinstance(i, B))
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

    def test_fork(self):
        self.a_count=0
        self.b_count = 0
        p=Pipe(
            Loop([A(),A()]),
            Fork(self.a_to_b,self.a_to_b,share=False,join=True),
            self.only_b

        )

        BotFrame.run()
        self.assertEqual(self.b_count,4)


