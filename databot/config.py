
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



config=Config()
