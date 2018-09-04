from .nodebase import Node
from .botframe import BotFrame




import typing

class Flat(Node):


    def __call__(self, message):
        if isinstance(message, typing.Iterable) and (not isinstance(message, (str, dict, tuple))):

            for i in message:
                yield i

        else:

            yield message




class SendTo(Node):

    def __init__(self,node):
        super().__init__()
        self.node=node
        self.target_q=None
        self.raw_bdata=True

    def init(self):

        b=BotFrame.bots[self.node_id]
        # self.target_q=b.iq[0]
        # return b.iq[0]

    def get_target_q(self):
        if self.target_q is not None:
            return self.target_q

        self.target_q=self.node.outer_iq
        return self.target_q
        # b=BotFrame.bots[self.node_id]
        # self.target_q=b.iq[0]
        # return b.iq[0]

    async def __call__(self, message,route_type=object):

        #get input q of node
        q=self.get_target_q()
        await q.put(message)



