import asyncio
class Config(object):

    Exception_default = 0
    Exception_raise=0
    Exception_ignore=1
    Exception_retry=2
    Exception_pipein = 3
    stream=0
    hierarchical=1
    def __init__(self):
        self.suppress_exception = False
        self.exception_policy=self.Exception_default
        self.joined_network=True
        self.execute_mode=self.stream
        self.replay_mode=False
        self.graph_optimize=True
        self.coroutine_batch_size=4  #for http loader the batch size don't effect time effort too much
        self.debug=False
        self.never_stop=False
        self.main_lock=asyncio.Lock()
        self.main_lock._locked=True
        self.check_stoping=True
        self.default_queue_max_size=1000
        self.backpressure_rate_limit=1000 #per sec


    def __repr__(self):
        return str(self.__dict__)



config=Config()
