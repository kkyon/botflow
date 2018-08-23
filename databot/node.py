import asyncio



class dotdict(dict):
     """dot.notation access to dictionary attributes"""
     __getattr__ = dict.get
     __setattr__ = dict.__setitem__
     __delattr__ = dict.__delitem__
class Node(object):

    def __init__(self,*args,**kwargs):
        self.args=args
        self.kwargs=dotdict(kwargs)
        self.init_param()

    async def init(self):
        await asyncio.sleep(0)
    async def close(self):
        await asyncio.sleep(0)

def node_debug(input):
    return input