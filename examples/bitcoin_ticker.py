from botflow import Pipe, Join, Pipe,Timer,Zip
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


httpload=HttpLoader(timeout=2)
ticker_pipes=[]
def parse_kraken(response):
    json=response.json
    t=Tick()
    t.exchange='kraken'
    t.bid=json['result']['XXBTZUSD']['b'][0]
    t.ask = json['result']['XXBTZUSD']['a'][0]
    t.time=time.time()
    return t


t_kraken=Pipe("https://api.kraken.com/0/public/Ticker?pair=XBTUSD", httpload, parse_kraken)
ticker_pipes.append(t_kraken)





def parse_bittrex(response):
    json=response.json
    t=Tick()
    t.exchange='bittrex'
    t.bid=json['result']['Bid']
    t.ask = json['result']['Ask']
    t.time=time.time()
    return t

t_bittrex=("https://bittrex.com/api/v1.1/public/getticker?market=USD-BTC", httpload, parse_bittrex)
ticker_pipes.append(t_bittrex)

def parse_bitstamp(response):
    json=response.json
    t=Tick()
    t.exchange='bitstamp'
    t.bid=float(json['bid'])
    t.ask=float(json['ask'])
    t.time=time.time()
    return t

t_bitstamp=Pipe("https://www.bitstamp.net/api/ticker/", httpload, parse_bitstamp)
ticker_pipes.append(t_bitstamp)




#https://api.bitfinex.com/v1/ticker/btcusd
def parse_bitfinex(response):
    json=response.json
    t=Tick()
    t.exchange='bitfinex'
    t.bid=float(json['bid'])
    t.ask=float(json['ask'])
    t.time=time.time()
    return t

t_bitfinex=Pipe("https://api.bitfinex.com/v1/ticker/btcusd", httpload, parse_bitfinex)
ticker_pipes.append(t_bitfinex)


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

t_bitpay=Pipe("https://bitpay.com/api/rates", httpload, parse_bitpay)
ticker_pipes.append(t_bitpay)




#http://api.coindesk.com/v1/bpi/currentprice.json

def parse_coindesk(response):
    json=response.json
    t=Tick()
    t.exchange='coindesk'
    t.bid = json['bpi']['USD']['rate_float']
    t.ask = t.bid
    t.time = time.time()
    return t
t_coindesk=Pipe("http://api.coindesk.com/v1/bpi/currentprice.json", httpload, parse_coindesk)
ticker_pipes.append(t_coindesk)


def main():


    Pipe(

        Timer(delay=2,max_time=5),
        Join(

            *ticker_pipes
        ),

        print
    )

    BotFlow.render('ex_output/bitcoin_arbitrage')
    BotFlow.run()



main()
