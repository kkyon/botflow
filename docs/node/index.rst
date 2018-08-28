Node
====

Node is callable thing .In python world ,we have three callable things ,

- function
- function object. class with override ```__call__```
- lambada


Major work  of user of databot  shouble be  writing core logic function,
for parsing, mapping,calculating , aggregating. It is the main purpose of databot desing.


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


.. toctree::
    :maxdepth: 1

    http
    db
    file
    util


