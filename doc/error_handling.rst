Exception Handling
==================

Exception Policies
~~~~~~~~~~~~~~~~~~

When an exception propagates outside of a hook handler, the hook group decides what to do according to its *exception propagation strategy*.

Setting the Active Policy
-------------------------

Setting the strategy is done with the :func:`gossip.set_exception_policy` function:

.. code-block:: python

		>>> import gossip
		>>> gossip.set_exception_policy(gossip.RaiseDefer())
		>>> gossip.set_exception_policy(gossip.RaiseImmediately())
		>>> gossip.set_exception_policy(gossip.IgnoreExceptions())

The policy can be changed per each hook group. The default is to inherit the behavior of the parent group. :func:`gossip.set_exception_policy` is merely an alias for :func:`gossip.groups.Group.set_exception_policy`.

Available Exception Handling Policies
-------------------------------------

The possible strategies that :func:`gossip.set_exception_policy` can receive are:

* :class:`gossip.RaiseImmediately() <gossip.exception_policy.RaiseImmediately>`: Raise upon the first exception encountered. **This is the default behavior for the global group**, and causes handlers to be skipped upon error.
* :class:`gossip.RaiseDefer() <gossip.exception_policy.RaiseDefer>`: Call all handlers, but raise the first exception encountered. This swallows intermediate errors, but at least tries to call as many handlers as possible.
* :class:`gossip.IgnoreExceptions() <gossip.exception_policy.IgnoreExceptions>`: This does nothing upon encountering errors, and calls all handlers always.
* :class:`gossip.Inherit() <gossip.exception_policy.Inherit>`: Takes the policy from the group's parent. You cannot set this policy for the global group, as it has no parent. **This is the default behavior for non-global groups**.

Handling Exceptions via the Built-in Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Gossip has predefined built-in hooks to handle various situations externally. One of those is ``gossip.on_handler_exception``. This is called for every exception raised from a handler, and allows you to intervene before Gossip moves on. One useful way to use this is to fire a debugger:

.. code-block:: python

		>>> @gossip.register('gossip.on_handler_exception')
		... def debugger(handler, exception, hook):
		...    exc_type, exc_value, exc_tb = exception
		...    import pdb
		...    pdb.post_mortem(exc_tb)

.. note:: Any exception raised from a handler for ``gossip.on_handler_exception`` will be propagated immediately. This is considered an internal error and no recovery is attempted. Be very careful when writing these handlers.
