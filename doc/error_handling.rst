Error Handling
==============

Exception Propagation
---------------------

When an exception propagates outside of a hook handler, the hook group decides what to do according to its *exception propagation strategy*.

Several such strategies exist:

1. Raise immediately (the default): the exception is raised immediately. This may cause uncalled handlers to be skipped
2. Raise after calling the remaining hooks: in this case, all handlers are attempted. The first exception encountered will be re-raised at the end.
3. Ignore: this ignores any exception that is raised from handlers. In this mode we always attempt all handlers.

Setting the strategy is done with the :func:`gossip.set_exception_policy` function:

.. code-block:: python

		>>> import gossip
		>>> gossip.set_exception_policy(gossip.RaiseDefer())
		>>> gossip.set_exception_policy(gossip.RaiseImmediately())
		>>> gossip.set_exception_policy(gossip.IgnoreExceptions())

The policy can be changed per each hook group. The default is to inherit the behavior of the parent group. :func:`gossip.set_exception_policy` is merely an alias for :func:`gossip.group.Group.set_exception_policy`.
