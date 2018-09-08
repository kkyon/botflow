replay
======

.. contents::
    :local:


When it work?
-------------

With ```config.replay_mode=True``` ,the Bot will turn replay mode.
when an exception is raised at step N, you don't need to run from setup 1 to N.
Botflow will replay the data from nearest completed node, usually step N-1.
It will save a lot of time in the development phase.

There are two mandatory condition for replay mode.

#.  Exception raised.
#.  Node completable. for unlimited stream pipe. it is unable to replay.

for below example .when restart application after exception raised, the double function will not be
executed any more.

.. code-block:: python

    from Botflow.flow import Pipe, Loop, Fork
    from Botflow.botframe import BotFrame
    from Botflow.config import config
    import time

    def double(a):
        print('double %d'%a)
        time.sleep(1)
        return 2*a


    count=0
    def triple(a):
        global  count
        count+=1
        if count>6:
            raise Exception()
            pass
        return 3*a

    #
    config.replay_mode=True

    def main():
        Pipe(

            Loop(range(10)),
            double,
            triple,
            print


        )

        BotFrame.run()



    main()



How it work?
------------
When exception raised , botframe will dump the cached data of the nearest completed node to disk.
it will restore from disk when restart. And the completed node of previous running  will not be start
again.

.. warning::

    Current version 0.1.7 ,in reply mode the data is cached in RAM.
    so not use when processing big data.






