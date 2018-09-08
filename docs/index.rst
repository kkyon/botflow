

Welcome to Botflow's world!
===================================




The Botflow applicaton is made with one or many pipes and run by ```BotFrame.run()```.
The simplest applicaton looks like:

.. code-block:: python

    Pipe(print)
    BotFrame.run()


Concept of the Botflow is very simple. ```I doubt if it is good to write a guide :-)```


**Pipe** works at the Top level. It combines the Node and Route together.

**Node** is callable: in python world, we have three callable things:

- function
- function object. Class with ```__call__``` function overridden
- lambada



**Route** is for duplicating data for multiple purposes. for simple applicaiton, you don't need route.
Just a main pipe.

case 1: when get a tick bitcoin price from api,
   you want save it to file and mysql at same time.

.. code-block:: python

    Pipe(
         get_price,
         Branch(save_to_db),
         save_to_file
    ）






case 2: crawler gets a google search result page. It may need to parse search result and next page link .


.. code-block:: python

      Pipe(
         "https://www.google.com/search?q=kkyon+Botflow",
         HttpLoader(),
         Branch(parse_search_result,save_to_db),
         parse_all_page_url,
         HttpLoader(),
         parse_search_result,
         save_to_db
      )


The above two code blocks look like pseudo code, but they are workable samples.

.. warning::

    In this documentationm. Data, Message, Event are the same thing.


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
