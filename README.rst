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

What's a Data-driven programming
====================



    Data-driven programming is a programming paradigm in which the program statements describe the data to be matched and the processing required rather than defining a sequence of steps to be taken.
    Standard examples of data-driven languages are the text-processing languages sed and AWK,where the data is a sequence of lines in an input stream.

    Data-driven programming is similar to event-driven programming, in that both are structured as pattern matching and resulting processing, and are usually implemented by a main loop, though they are typically applied to different domains.

    Data-driven programming is typically applied to streams of structured data, for filtering, transforming, aggregating (such as computing statistics), or calling other programs

    Databot have few basic concept to impelement DDP.
- **Pipe**
   it is the main stream process of the programe . all unit will work inside.
- **Node**
        it is the process logic node . it will driven by data. custom function work as Node .
        There are some built-in node  :
   * Loop:work as **for**
   * Timer: it will send message in the pipe by timer param . **delay**, **max_time**
   * HttpLoader: get a url and return Httpresponse
   * Mysql query or insert: for mysql querying and insert
   * File read write: for file write.
- **Route**
        It will be used to create complex data flow network,not just only one main process. Databot can nest Route in side a Route.
        it would very powerfull.
        There are some pre built-in Route:
 * **Branch** : will duplicte data from parent pipe to a branch .
 * **Return** : will duplicate data from parent pipe, and return finally result to parent pipe.
 * **Filter** : drop out data from pipe by some condition
 * **Fork** : will duplicate data to many branch.
 * **Join** : duplicate data to many branches ,and return result to pipe.


All unit(Pipe,Node,Route) communicates via queue and paralle in coroutine . but User of the databot not care too much the detail of asyncio .

Below some graphes will get you some basic concept for the Route:

    .. image:: path/filename.png



Databot is...
=============

- **Simple**

    Databot is easy to use and maintain, and does *not need configuration files* and know about asynckio .

    It has an active, friendly community you can talk to for support,

    Here's one of the simplest applications you can make::
   
   .. code-block:: python

    from databot.flow import Pipe, Loop, Fork,Join,Branch,BlockedJoin,Return
    from databot import flow
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



    config.exception_policy=config.Exception_ignore
    def main():


        hget=HttpLoader(timeout=2)

        Pipe(

            flow.Timer(delay=3,max_time=5),
            BlockedJoin(
                Return("https://api.kraken.com/0/public/Ticker?pair=XBTUSD", hget, parse_kraken),
                Return("https://bittrex.com/api/v1.1/public/getticker?market=USD-BTC", hget, parse_bittrex),

            ),
            print,

        )

        BotFrame.render('bitcoin_arbitrage')
        BotFrame.run()



    main()


- **Fast**

    Node will be run in parallel ,and it will get high performance
    when processing stream data.



- **Visualliztion**



Contributing
------------




Donate
------




Links
-----
