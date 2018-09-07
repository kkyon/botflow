from unittest import TestCase
import typing
import asyncio



class TestPython(TestCase):


    def test_callable(self):
        class A:
            pass

        class B:
            def __call__(self, *args, **kwargs):
                pass

        def f():
            pass
        async def af():
            await asyncio.sleep()
        self.assertTrue(isinstance(f,typing.Callable))
        self.assertTrue(isinstance(lambda r:r, typing.Callable))
        self.assertTrue(isinstance(af, typing.Callable))
        self.assertFalse(isinstance([], typing.Callable))
        self.assertFalse(isinstance('', typing.Callable))
        self.assertFalse(isinstance(1, typing.Callable))
        self.assertTrue(isinstance(A, typing.Callable))
        self.assertTrue(isinstance(B, typing.Callable))
        self.assertFalse(isinstance(A(), typing.Callable))
        self.assertTrue(isinstance(B(), typing.Callable))


    def test_iterable(self):
        def f():
            yield 1
        self.assertTrue(isinstance([],typing.Iterable))
        self.assertTrue(isinstance((), typing.Iterable))
        self.assertTrue(isinstance((), typing.Tuple))
        self.assertTrue(isinstance([], typing.List))
        self.assertTrue(isinstance(f(), typing.Iterable))
        self.assertTrue(isinstance(f(), typing.Generator))