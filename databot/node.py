class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Node(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = dotdict(kwargs)
        self.ref = 0
        self.inited = False
        self.closed = False
        self.init_param()

    def init_param(self):
        pass

    async def init(self):
        raise NotImplemented()

    async def close(self):
        raise NotImplemented()

    async def node_init(self):
        self.ref += 1
        if self.inited == True:
            return
        await self.init()

    async def node_close(self):
        self.ref -= 1
        if self.ref > 0 or self.closed == True:
            return
        self.closed = True
        await self.close()


def node_debug(input):
    return input
