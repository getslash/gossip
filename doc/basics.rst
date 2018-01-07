Basic Usage
===========

Gossip is all about defining entry points, called hooks, that follow the `Observer pattern <http://en.wikipedia.org/wiki/Observer_pattern>`_. A hook can be defined, have functions (or handlers) registered to it, and then triggered at some point to notify the observers of an event. 

All hooks in gossip must be identified by a **name**, which uniquely identifies the hook.

Registering Handlers
--------------------

To register a handler for a hook, just use :py:func:`gossip.register`:

.. code-block:: python

		>>> from __future__ import print_function
		>>> import gossip
		
		>>> @gossip.register('hook_name')
		... def func():
		...     print('Called')

:py:func:`gossip.registered` context can be used to specify a temporarily registered handler around a specific code block

.. code-block:: python

		>>> def func2():
		...     print('Func2')

		>>> with gossip.registered('hook_name', func2) as reg:
		...     assert reg.is_active()
		>>> assert not reg.is_active()

Triggering Hooks
----------------

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

		>>> gossip.get_hook('hook_name').unregister_all()


