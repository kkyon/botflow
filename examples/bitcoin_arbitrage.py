from databot.flow import Pipe, Loop, Fork,Join,Branch,BlockedJoin,Return
from databot import flow
from databot.botframe import BotFrame
from databot.http.http import HttpLoader
import asyncio
import time
import datetime
from databot.config import config
class Tick(object):


    def __init__(self):
        self.ask=None
        self.bid=None
        self.exchange=''
        self.time=None
    def __repr__(self):

        st = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S')
        return "{} {} ask:{} bid:{}".format(self.exchange,st,self.ask,self.bid)

# <pair_name> = pair name
#     a = ask array(<price>, <whole lot volume>, <lot volume>),
#     b = bid array(<price>, <whole lot volume>, <lot volume>),
#     c = last trade closed array(<price>, <lot volume>),
#     v = volume array(<today>, <last 24 hours>),
#     p = volume weighted average price array(<today>, <last 24 hours>),
#     t = number of trades array(<today>, <last 24 hours>),
#     l = low array(<today>, <last 24 hours>),
#     h = high array(<today>, <last 24 hours>),
#     o = today's opening price
# {"error":[],"result":{"EOSUSD":{
# "a":["5.056500","232","232.000"],
# "b":["5.037300","50","50.000"],
# "c":["5.049100","196.38370000"],"v":["152013.19766895","160019.03280639"],"p":["4.937054","4.941003"],"t":[746,808],"l":["4.777800","4.777800"],"h":["5.102306","5.102306"],"o":"4.897100"}}}


def parse_kraken(response):
    json=response.json
    t=Tick()
    t.exchange='kraken'
    t.bid=json['result']['XXBTZUSD']['b'][0]
    t.ask = json['result']['XXBTZUSD']['a'][0]
    t.time=time.time()
    return t




#https://bittrex.com/api/v1.1/public/getticker?market=USD-BTC
#{"success":true,"message":"","result":{"Bid":6735.45300000,"Ask":6736.28600000,"Last":6735.45300000}}
def parse_bittrex(response):
    json=response.json
    t=Tick()
    t.exchange='bittrex'
    t.bid=json['result']['Bid']
    t.ask = json['result']['Ask']
    t.time=time.time()
    return t

#https://www.bitstamp.net/api/ticker/
#{"high": "6771.10000000", "last": "6717.09", "timestamp": "1535158781", "bid": "6714.00", "vwap": "6570.95", "volume": "6558.77569484", "low": "6445.32000000", "ask": "6717.09", "open": 6692.99}
def parse_bitstamp(response):
    json=response.json
    t=Tick()
    t.exchange='bitstamp'
    t.bid=float(json['bid'])
    t.ask=float(json['ask'])
    t.time=time.time()
    return t

config.exception_policy=config.Exception_ignore
def main():
    Pipe(

        flow.Timer(delay=3,max_time=5),
        Join(
            Return("https://api.kraken.com/0/public/Ticker?pair=XBTUSD", HttpLoader(), parse_kraken),
            Return("https://bittrex.com/api/v1.1/public/getticker?market=USD-BTC", HttpLoader(), parse_bittrex),
            Return("https://www.bitstamp.net/api/ticker/", HttpLoader(), parse_bitstamp),
        ),
        print,






    )

    BotFrame.render('bitcoin_arbitrage')
    BotFrame.run()



main()
