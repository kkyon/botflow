Node
====

.. contents::
    :local:

Node is callable thing .In python world ,we have three callable things ,

- function
- function object. class with override ```__call__```
- lambada


Major work  of user of Botflow  shouble be  writing core logic function,
for parsing, mapping,calculating , aggregating. It is the main purpose of Botflow desing.


Pass into Node:
---------------
Node must have only one parameter. the pass in value is from upflow node return value.


Return from Node:
-----------------
Node can return anything . list ,generator,raw value,tuple  .

.. attention::

    - list will be unpacked into separate item . tuple will not be unpacked.
    - generator will be iterated by bot. so you can return a infinite generator to simulate a stream flow
      it is interested to test.
    - raw will put into queue.

How to handle Excpetion:
------------------------

Exception behavior will act according to ```config.Exception_policy = config.Exception_raise ``` setting.

:Exception_default: default exception policy is raise
:Exception_raise: raise exception
:Exception_ignore: ignore exception. exception raised from node will be suppressed.
:Exception_retry:   the value will put in input-queue after some delay.
:Exception_pipein: the exception tread as returen value ,put in output queue. it will be usefull
                       in blockedjoin route scenarios.



.. contents::
    :local:


Timer
------

    It will send a message in the pipe by timer param. delay, max_time until some finished

```Timer(self, delay=1, max_time=None, until=None)```


:dealy:  the delay between every count
:max_time: will stop when reach the max count time.
:until: the function ref. Timer will count until function return True.


HttpLoader
-----------

    Get a url and return the HTTP response

    Init parameter
    --------------

    :timeout:
            default timeout=20 .

    Callable parameter:
    ------------------

    can be call by string (url), and Httprequest.

    HttpResponse
    ------------
    HttpResponse


    :json: return a json object
    :text: get text body of the httpresponse
    :xml:  get lxml object
    :css: get css object


    HttpRequest
    ------------

    :head:
    :body:
    :url:
    :proxy:



AioFile
----------------
    for file I/O.

SpeedLimit
----------

    limit the stream speed limit

Delay
------

    delay in special second.
Zip
-----
    Wait for all branched to finish and merged the result into a tuple.

Filter
-----

    Drop data from pipe if it does not match some condition


