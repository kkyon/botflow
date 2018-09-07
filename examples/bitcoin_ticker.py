from botflow import Pipe, Join, Return,Timer,Zip
from botflow import BotFlow
from botflow.ex.http import HttpLoader
import time
import datetime
from botflow.config import config
from botflow.node import print_list
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

def parse_bitstamp(response):
    json=response.json
    t=Tick()
    t.exchange='bitstamp'
    t.bid=float(json['bid'])
    t.ask=float(json['ask'])
    t.time=time.time()
    return t

#https://api.bitfinex.com/v1/ticker/btcusd
def parse_bitfinex(response):
    json=response.json
    t=Tick()
    t.exchange='bitfinex'
    t.bid=float(json['bid'])
    t.ask=float(json['ask'])
    t.time=time.time()
    return t
#https://bitpay.com/api/rates
def parse_bitpay(response):
    json=response.json
    t=Tick()
    t.exchange='bitpay'
    for p in json:
        if p['code']=='USD':
            t.bid=p['rate']
            t.ask=t.bid
            t.time=time.time()

            return t
#http://api.coindesk.com/v1/bpi/currentprice.json

def parse_coindesk(response):
    json=response.json
    t=Tick()
    t.exchange='coindesk'
    t.bid = json['bpi']['USD']['rate_float']
    t.ask = t.bid
    t.time = time.time()
    return t

config.exception_policy=config.Exception_pipein

def main():

    httpload=HttpLoader(timeout=2)
    Pipe(

        Timer(delay=2,max_time=5),
        Join(
            Return("https://api.kraken.com/0/public/Ticker?pair=XBTUSD",httpload , parse_kraken),
            Return("https://bittrex.com/api/v1.1/public/getticker?market=USD-BTC", httpload, parse_bittrex),
            Return("https://www.bitstamp.net/api/ticker/", httpload, parse_bitstamp),
            Return("https://api.bitfinex.com/v1/ticker/btcusd", httpload, parse_bitfinex),
            Return("https://bitpay.com/api/rates", httpload, parse_bitpay),
            Return("http://api.coindesk.com/v1/bpi/currentprice.json", httpload, parse_coindesk),



        ),

        Zip(n_stream=6),
        print_list

    )

    BotFlow.render('ex_output/bitcoin_arbitrage')
    BotFlow.run()



main()
