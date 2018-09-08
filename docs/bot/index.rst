Bot
============




.. toctree::
    :maxdepth: 1

    replay

.. contents::
    :local:


Run
---

Exception
---------


Exception behavior will act according to ```config.Exception_policy = config.Exception_raise ``` setting.

:Exception_default: default exception policy is raise
:Exception_raise: raise exception
:Exception_ignore: ignore exception. exception raised from node will be suppressed.
:Exception_retry:   the value will put in input-queue after some delay.
:Exception_pipein: the exception tread as returen value ,put in output queue. it will be usefull
                       in blockedjoin route scenarios.


How to debug
------------

