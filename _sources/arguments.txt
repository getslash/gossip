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

