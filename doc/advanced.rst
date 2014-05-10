Advanced Usage
==============

Hook Arguments
--------------

Hooks can receive arguments, which are then passed to the handlers. 

.. code-block:: python
   
		>>> import gossip

		>>> @gossip.register("with_arguments")
		... def handler(a, b, c):
		...     print("Called:", a, b, c)
		
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



Defining Hooks Explicitly
-------------------------

By default, registering hooks in with :func:`gossip.register` takes care of hook definition and registration at the same time. In several cases, however, you may want to simply define a hook, but not register anything to it yet. For this we have the :func:`gossip.define` API:

.. code-block:: python

		>>> import gossip
		>>> hook = gossip.define('hook_name_here')
		>>> @hook.register
		... def handler():
		...     pass

The :func:`gossip.register` returns the :class:`gossip.hook.Hook` object for the defined hook, so further operations can be executed against it.

Hooks cannot be ``define``-d more than once:

.. code-block:: python

		>>> import gossip
		>>> hook = gossip.define('some_hook')
		>>> gossip.define('some_hook') # doctest: +IGNORE_EXCEPTION_DETAIL
		Traceback (most recent call last):
		   ...
		NameAlreadyUsed: ...

Getting Hooks by Name
---------------------

Once a hook is defined you can get the underlying :class:`gossip.hook.Hook` object by using :func:`gossip.get_hook`:

.. code-block:: python

		>>> gossip.get_hook('some_hook')
		<Hook some_hook()>

However, in this way the hook is never defined for you:

.. code-block:: python

		>>> gossip.get_hook('nonexisting_hook') # doctest: +IGNORE_EXCEPTION_DETAIL
		Traceback (most recent call last):
		   ...
		HookNotFound: ...
		

