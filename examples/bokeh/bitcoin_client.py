from botflow import *
from botflow import BotFlow
from botflow.ex.http import HttpLoader

import time
import datetime
from botflow.config import config


class Tick(object):

    def __init__(self):
        self.ask = None
        self.bid = None
        self.exchange = ''
        self.time = None

    def __repr__(self):
        st = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S')
        return "{} {} ask:{} bid:{}".format(self.exchange, st, self.ask, self.bid)


httpload=HttpLoader(timeout=2)
ticker_pipes={}
def parse_kraken(response):
    json=response.json
    t=Tick()
    t.exchange='kraken'
    t.bid=json['result']['XXBTZUSD']['b'][0]
    t.ask = json['result']['XXBTZUSD']['a'][0]
    t.time=time.time()
    return t


t_kraken=Pipe("https://api.kraken.com/0/public/Ticker?pair=XBTUSD", httpload, parse_kraken)
ticker_pipes['kraken']=t_kraken





def parse_bittrex(response):
    json=response.json
    t=Tick()
    t.exchange='bittrex'
    t.bid=json['result']['Bid']
    t.ask = json['result']['Ask']
    t.time=time.time()
    return t

t_bittrex=Pipe("https://bittrex.com/api/v1.1/public/getticker?market=USD-BTC", httpload, parse_bittrex)
ticker_pipes['bittrex']=t_bittrex

def parse_bitstamp(response):
    json=response.json
    t=Tick()
    t.exchange='bitstamp'
    t.bid=float(json['bid'])
    t.ask=float(json['ask'])
    t.time=time.time()
    return t

t_bitstamp=Pipe("https://www.bitstamp.net/api/ticker/", httpload, parse_bitstamp)
ticker_pipes['bitstamp']=t_bitstamp



config.exception_policy = config.Exception_ignore





import datetime

from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.client import push_session
from bokeh.plotting import figure, curdoc
from bokeh.palettes import Category20

source_dict={}
p = figure( y_range=(6400, 6500))
p.xaxis.formatter=DatetimeTickFormatter()
idx=1
for k,v in ticker_pipes.items():
    source_dict[k]=ColumnDataSource(data=dict(x=[], y=[]))
    p.line(x='x', y='y', source=source_dict[k], color=Category20[20][idx], legend=k)
    idx+=1



session = push_session(curdoc(), session_id='main')

session.show(p) # open the document in a browser

def push_price(d:Tick):
    timestamp = datetime.datetime.fromtimestamp(d.time)
    source_dict[d.exchange].stream(dict(x=[timestamp], y=[d.bid]))


def main():


    p = Pipe(

        Timer(delay=3),

        Join(
            *[v for k,v in ticker_pipes.items()],


        ),
        Branch(print),
        push_price,



    )

    p.run()


main()
