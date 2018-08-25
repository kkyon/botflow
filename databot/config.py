
class Config(object):

    Exception_raise=0
    Exception_ignore=1
    Exception_retry=2
    stream=0
    hierarchical=1
    def __init__(self):
        self.suppress_exception = False
        self.exception_policy=self.Exception_raise
        self.joined_network=True
        self.execute_mode=self.stream



config=Config()
