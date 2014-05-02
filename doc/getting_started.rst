Getting Started
===============

Gossip is all about defining entry points, called hooks, that follow the `Observer pattern <http://en.wikipedia.org/wiki/Observer_pattern>`_. A hook can be defined, have functions (or handlers) registered to it, and then triggered at some point to notify the observers of an event. 

All hooks in gossip must be identified by a **name**, which uniquely identifies the hook.

A Basic Example
---------------

To register a handler for a hook, just user :py:func:`gossip.register`:

.. code-block:: python

		>>> import gossip
		
		
		>>> @gossip.register('hook_name')
		... def func():
		...     print('Called')

After we registered the handler, we can trigger it at any time:

.. code-block:: python

		>>> gossip.trigger('hook_name')
		Called


Unregistering Handlers
----------------------

Handlers can be easily unregistered by calling ``.gosip.unregister()`` on them:

.. code-block:: python

		>>> func.gossip.unregister()

And you can also unregister all handler on a specific hook:

.. code-block:: python

		>>> gossip.unregister_all('hook_name')

