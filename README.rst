===========================
Databot
===========================

* Data driven programming framework .
* Paralleled in coroutines .
* Type and content based route function.


Installing
----------

Install and update using `pip`_:


**pip install -U databot**

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
   * **Loop**:work as **for**
   * **Timer**: it will send message in the pipe by timer param . **delay**, **max_time**
   * **HttpLoader**: get a url and return Httpresponse
   * **Mysql query or insert**: for mysql querying and insert
   * **File read write**: for file write.
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
      branch:https://github.com/kkyon/databot/blob/master/docs/databot_branch.jpg
      fork:https://github.com/kkyon/databot/blob/master/docs/databot_fork.jpg
      join:https://github.com/kkyon/databot/blob/master/docs/databot_join.jpg
      return:https://github.com/kkyon/databot/blob/master/docs/databot_return.jpg
      
 



Databot is...
=============

- **Simple**

Databot is easy to use and maintain, and does *not need configuration files* and know about asynckio .

It has an active, friendly community you can talk to for support,

Here's one of the simple applications you can make.load the bitoin prices every 2 sencond.advantage price aggreagator sample can be found here.
    https://github.com/kkyon/databot/tree/master/examples


   
.. code-block:: python

    from databot.flow import Pipe,Timer
    from databot.botframe import BotFrame
    from databot.http.http import HttpLoader


    def main():
        Pipe(

            Timer(delay=2),
            "http://api.coindesk.com/v1/bpi/currentprice.json",
            HttpLoader(),
            lambda r:r.json['bpi']['USD']['rate_float'],
            print,
        )

        BotFrame.render('simple_bitcoin_price')
        BotFrame.run()

    main()



.. image:: https://github.com/kkyon/databot/raw/master/examples/simple_bitcoin_price.png
  :width: 200
  :alt: simple_bitcoin_price

- **Fast**
Node will be run in parallel ,and it will get high performance
when processing stream data.



- **Visualliztion**
with render function . **BotFrame.render('bitcoin_arbitrage')**. databot will render the data flow network  into a graphiz image. 

- **Replay-able**
with replay mode enable  **config.replay_mode=True** . when raise excpeiton raise in step N ,you no need to run again from setup 1 to N .databot will replay the
data from nearest completed node ,usally step N-1 . it will save a lot time in development phase .




Contributing
------------




Donate
------




Links
-----
