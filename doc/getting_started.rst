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

Handlers can be easily unregistered by calling ``.gossip.unregister()`` on them:

.. code-block:: python

		>>> func.gossip.unregister()

And you can also unregister all handler on a specific hook:

.. code-block:: python

		>>> import gossip.registry
		>>> gossip.registry.unregister_all('hook_name')


Explicit vs. Implicit Definition of Hooks
-----------------------------------------

By default, registering hooks in with :func:`gossip.register` takes care of hook definition and registration at the same time. In several cases, however, you may want to simply define a hook, but not register anything to it yet. For this we have the :func:`gossip.define` API:

.. code-block:: python

		>>> import gossip
		>>> hook = gossip.define('hook_name_here')
		>>> @hook.register
		... def handler():
		...     pass

The :func:`gossip.register` returns the :class:`gossip.hook.Hook` object for the defined hook, so further operations can be executed against it.

Hooks cannot be ``define``d more than once:

.. code-block:: python

		>>> import gossip
		>>> hook = gossip.define('some_hook')
		>>> gossip.define('some_hook') # doctest: +IGNORE_EXCEPTION_DETAIL
		Traceback (most recent call last):
		   ...
		NameAlreadyUsed: ...
