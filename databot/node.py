class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class CountRef(object):
    def __init__(self):
        self.count=0

    def incr(self):
        self.count=self.count+1
        return self.count

    def decr(self):

        self.count=self.count-1

        return self.count

class Node(CountRef):
    boost_by_thread=1
    boost_by_process=2
    #boost_by_cluster=3
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = dotdict(kwargs)

        self.inited = False
        self.closed = False
        self.init_param()
        super().__init__()

    def init_param(self):
        pass



    async def node_init(self):
        if self.incr() == 1:
            await self.init()


    async def node_close(self):
        if self.decr() == 0:
            await self.close()

    @classmethod
    def boost(cls,f):


        f.boost_type=type

        return f


    @classmethod
    def boost_type(cls,type=boost_by_thread):

        def wrap(f):
            f.boost_type=type

            return f


        return wrap



def node_debug(input):
    return input
