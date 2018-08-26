===========================
Databot
===========================

    *data driven programming framework with asyncio.
    *it hided complex async programming detail .every processor unit will act like a bot .
    *The framework also provider type and content base route function.


Installing
----------

Install and update using `pip`_:


    pip install -U databot


A Simple Example
----------------

.. code-block:: python


    from databot.flow import Pipe, Loop, Fork
    from databot.botframe import BotFrame


    class Sum(object):

        def __init__(self):
            self.sum = 0

        def __call__(self, i):
            self.sum += i
            return self.sum

        def __repr__(self):
            return 'sum:' + str(self.sum)


    op_sum = Sum()


    def main():
        Pipe(

            Loop(range(1000000)),
            Fork(op_sum),
            print

        )

        BotFrame.run()
        print(op_sum)


    main()


A Spider(crawler) Example
----------------
.. code-block:: python


    from databot.flow import Pipe, Loop, Fork,Join,Branch,BlockedJoin,Return,Timer
    from databot.botframe import BotFrame
    from databot.http.http import HttpLoader
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

            Timer(delay=10,max_time=5),
            BlockedJoin(
                Return("https://api.kraken.com/0/public/Ticker?pair=XBTUSD",httpload , parse_kraken),
                Return("https://bittrex.com/api/v1.1/public/getticker?market=USD-BTC", httpload, parse_bittrex),
                Return("https://www.bitstamp.net/api/ticker/", httpload, parse_bitstamp),
                Return("https://bitpay.com/api/rates", httpload, parse_bitpay),
                Return("http://api.coindesk.com/v1/bpi/currentprice.json", httpload, parse_coindesk),
            ),
            print,
        )

        BotFrame.render('bitcoin_arbitrage')
        BotFrame.run()



    main()

.. code-block:: text




Contributing
------------




Donate
------




Links
-----