# -*- coding: utf-8 -*-

import asyncio
import os
import sys

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt.async_support as ccxt  # noqa: E402

class OrderBook(object):
    def __init__(self):
        self.bids=[]
        self.asks=[]
        self.timestamp=None
        self.datetime=None
        self.nonce=None


class Ticker(object):

    def __init__(self):
        self.symbol=None
        self.timestamp=None
        self.datetime=None
        self.high=None
        self.low=None
        self.bid=None
        self.bidVolume=None
        self.ask=None
        self.askVolume=None
        self.vwap=None
        self.open=None
        self.close=None
        self.last=None
        self.previousClose=None
        self.change=None
        self.percentage=None
        self.average=None
        self.baseVolume=None
        self.quoteVolume=None
        self.info=None

    def __repr__(self):
        return "{}({})".format(self.__class__,self.symbol)

class Trade(object):

    def __init__(self):
        self.id=None
        self.order=None
        self.info=None
        self.timestamp=None
        self.datetime=None
        self.symbol=None
        self.type=None
        self.side=None
        self.price=None
        self.amount=None
        self.cost=None
        self.fee=None


async def cxxt_tickers(ccxt_ex:ccxt.Exchange):
        t=await  ccxt_ex.fetch_tickers()

        result=[]
        for s,t in t.items():
            ticker = Ticker()
            for k,v in t.items():

                ticker.__dict__[k]=v
            result.append(ticker)
        return result







async def gdax():
    ex = ccxt.kraken()
    markets = await cxxt_tickers(ex)
    await ex.close()
    return markets

if __name__ == '__main__':
    print(asyncio.get_event_loop().run_until_complete(gdax()))