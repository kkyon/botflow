

class Config:
    def __init__(self):
        self._max_size=128

    @property
    def max_size(self):
        print('get max %s',self._max_size)
        return self._max_size

    @max_size.setter
    def max_size(self,v):

        self._max_size=v
        print('set max %s', self._max_size)

config=Config()


def init(max_size=config.max_size):
    print("max_size %s",max_size)


class Queue(object):
    def __init__(self,max_size=config.max_size):
        print("Queue max_size %s", max_size)


config.max_size=0

init()
Queue()