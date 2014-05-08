Using Gossip
============

Gossip is all about defining entry points, called hooks, that follow the `Observer pattern <http://en.wikipedia.org/wiki/Observer_pattern>`_. A hook can be defined, have functions (or handlers) registered to it, and then triggered at some point to notify the observers of an event. 

All hooks in gossip must be identified by a **name**, which uniquely identifies the hook.

A Basic Example
---------------

To register a handler for a hook, just user :py:func:`gossip.register`:

.. code-block:: python

		>>> from __future__ import print_function
		>>> import gossip
		
		
		>>> @gossip.register('hook_name')
		... def func():
		...     print('Called')

After we registered the handler, we can trigger it at any time:

.. code-block:: python

		>>> gossip.trigger('hook_name')
		Called


Hook Arguments
--------------

Hooks can receive arguments, which are then passed to the handlers. 

.. code-block:: python
   
		>>> @gossip.register("with_arguments")
		... def handler(a, b, c):
		...     print("Called: {0} {1} {2}".format(a, b, c))
		
		>>> gossip.trigger("with_arguments", a=1, b=2, c=3)
		Called: 1 2 3

Note that argument mismatches means a runtime error:

.. code-block:: python
		
		>>> gossip.trigger("with_arguments", a=1) # doctest: +IGNORE_EXCEPTION_DETAIL
		Traceback (most recent call last):
		 ...
		TypeError: handler() takes exactly 3 arguments (1 given)

.. note::
   Since hook handlers are likely to be spread across many locations in your projects, argument ordering changes make your code more likely to break. This is why gossip forces all arguments to be passed by keywords, and not as positionals.

