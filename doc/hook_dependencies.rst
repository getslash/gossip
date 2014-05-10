Hook Dependencies
=================

In most projects you are likely to bind multiple handlers to each hook. As you further separate different services to modules and decouple complex code, you may encounter cases in which a handler needs to execute *only after* another handler has finished. This sounds trivial, but it gets tricky as you take into account module load order.

By default, Gossip executes handlers by order of registration:

.. code-block:: python

		>>> import gossip

		>>> @gossip.register("handler")
		... def handler1():
		...     print("Handler 1 called")

		>>> @gossip.register("handler")
		... def handler2():
		...     print("Handler 2 called")

		>>> gossip.trigger("handler")
		Handler 1 called
		Handler 2 called

Now let's separate the two registrations to two separate modules:


**module1.py:**

.. code-block:: python

		@gossip.register("handler")
		def handler1():
		    print("Handler 1 called")

**module2.py:**

.. code-block:: python

		@gossip.register("handler")
		def handler2():
		    print("Handler 2 called")


Now the results of your program vary unexpectedly depending on your import order:

.. code-block:: python

		# in this case, handler1 registers first, and so will be triggered first
		import module1
		import module2

.. code-block:: python

		# in this case, handler2 registers first, and so will be triggered first
		import module2
		import module1

Gossip aims to help you with such issues, and still leave you with the ability to register handlers from anywhere in your code.

Using the Signaling Helpers
---------------------------

Gossip offers a few helper functions to assist with dependency resolution. These helpers all abort the current execution of the handler via an exception, and signal Gossip to try again after other hooks are called.

wait_for
~~~~~~~~

:func:`gossip.wait_for` receives a boolean expression and defers execution if it is ``False``y:

.. code-block:: python

		>>> second_handler_called = False

		>>> @gossip.register("hook1")
		... def first_handler():
		...     gossip.wait_for(second_handler_called)
		...     print("First handler")
		
		>>> @gossip.register("hook1")
		... def second_handler():
		...     global second_handler_called
		...     second_handler_called = True
		...     print("Second handler")

		>>> gossip.trigger("hook1")
		Second handler
		First handler

not_now
~~~~~~~

:func:`gossip.not_now` defers execution, and is a different way of writing ``gossip.wait_for(False)``:

.. code-block:: python

		>>> @gossip.register("hook1")
		... def handler():
		...     if not some_condition():
		...         gossip.not_now()
