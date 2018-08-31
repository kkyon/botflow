

Welcome to databot's world!
===================================




The databot applicaton are made with one or many pipes. and run by ```BotFrame.run()```.
The simplest applicaton like this :

.. code-block:: python

    Pipe(print)
    BotFrame.run()


Concept of the databot very simple. ```I doubt if it is good to write a guide :-)```


**Pipe** work at the Top level .It combine the node,Route,together.

**Node** is callable :In python world ,we have three callable thing ,

- function
- function object. class with override ```__call__```
- lambada



**Route** is for duplicating data for multiple purposes. for simple applicaiton ,you don't need route.
Just a main pipe.

case 1: when get a tick bitcoin price from api ,
   you want save it to file and mysql at same time.

.. code-block:: python

    Pipe(
         get_price,
         Branch(save_to_db),
         save_to_file
    ）






case 2: crawler get a google search result page . it maybe need to parse search result and next page link .


.. code-block:: python

      Pipe(
         "https://www.google.com/search?q=kkyon+databot",
         HttpLoader(),
                           Branch(parse_search_result,save_to_db),
         parse_all_page_url,
         HttpLoader(),
         parse_search_result,
         save_to_db

      )


up two code block look like fake code. but they are true sample.

.. warning::

    In this document Data,Message ,Event are the same thing.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   bot/index
   pipe/index
   node/index
   route/index
   change/0.1.8

.. toctree::
    :maxdepth: 1

    faq





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
