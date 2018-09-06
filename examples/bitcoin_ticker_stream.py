from botflow import Pipe, Join, Return,Timer,Branch
from botflow import BotFlow
from botflow.ex.http import HttpLoader

import time
import datetime
from botflow.config import config


class Tick(object):


    def __init__(self):
        self.ask=None
        self.bid=None
        self.exchange=''
        self.time=None
    def __repr__(self):
        st = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S')
        return "{} {} ask:{} bid:{}".format(self.exchange,st,self.ask,self.bid)

def parse_kraken(response):
    json=response.json
    t=Tick()
    t.exchange='kraken'
    t.bid=json['result']['XXBTZUSD']['b'][0]
    t.ask = json['result']['XXBTZUSD']['a'][0]
    t.time=time.time()
    return t

def parse_bittrex(response):
    json=response.json
    t=Tick()
    t.exchange='bittrex'
    t.bid=json['result']['Bid']
    t.ask = json['result']['Ask']
    t.time=time.time()
    return t



config.exception_policy=config.Exception_ignore

def print_list(d:list):
    print(d)
    return d

def main():


    hget=HttpLoader(timeout=2)

    Pipe(

        Timer(delay=3,max_time=5),

        Join(
            Return("https://api.kraken.com/0/public/Ticker?pair=XBTUSD", hget, parse_kraken),
            Return("https://bittrex.com/api/v1.1/public/getticker?market=USD-BTC", hget, parse_bittrex),

        ),
        print,

    )

    BotFlow.render('ex_output/bitcoin_arbitrage')
    BotFlow.run()



main()
