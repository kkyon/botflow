Route
=====

.. contents::
    :local:

Route is important concept of the Botflow. With it ,we can duplicate ,join,drop data.
and route message to muliti target Node.

```def __init__(self, *args, route_type=object,route_func=None, share=True, join=False):```


:args: list of Node or Route.

:share: True|False. default value *True*  if keep the orignal data for upflow.

:route_type: list of Type for route upflow message to Branch.default value *object*

:route_func: a function handle for route. logic bewteen route_type and route_func work together with `and`.

:join: True|False  ,if Return the final message to parent  Pipe. default value *False*



Branch
------
    most Basic route of the Botflow .it duplicate the parent from the parent pipe.


Return
------
    Route Return is derived from Branch with parameter (share=False,join=True)

    Branch,Return,Filter
    ====================


    .. image:: Botflow_branch.jpg
        :width: 300



    :share: True|False.  if keep the orignal data for parent pipe

    :route_type: list of Type for route upflow message to Branch

    :join: True|False  ,if Return the final message to parent  Pipe.



Filter
------
    Route Filter is derived from Branch .it will drop out message ,if not match (route_type,route_func)
    sametime.


Join
----
    Join is derived from Fork with parameter(share=False,join=True) .


SendTo
------
     Send the stream to speicaled Node.
