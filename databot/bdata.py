



class BotControl(object):
    pass


class Retire(BotControl):
    pass


class Suspend(BotControl):
    pass


class Resume(BotControl):
    pass


class ChangeIq(BotControl):

    def __init__(self, iq_num=128):
        self.iq_num = iq_num


class Bdata:
    __slots__ = ['ori','data','meta']

    def __init__(self,data,ori=0):
        if isinstance(data,Bdata):
            raise Exception('not right data'+str(data))
        self.data=data
        self.meta=None
        self.ori=ori

    def __repr__(self):
        return str(self.data)


    def is_BotControl(self):

        return isinstance(self.data,BotControl)

    @classmethod
    def make_Retire(cls):
        return Bdata(Retire())