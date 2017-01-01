Managing Hook Dependencies
==========================

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

Gossip aims to help you with such issues, and still leave you with the ability to register handlers from anywhere in your code. It provides two main ways of controlling hook dependencies: Signaling helpers and needs/provides markers.

Using the Signaling Helpers
---------------------------

Gossip offers a few helper functions to assist with dependency resolution. These helpers all abort the current execution of the handler via an exception, and signal Gossip to try again after other hooks are called.

wait_for
~~~~~~~~

:func:`gossip.wait_for` receives a boolean expression and defers execution if it is ``False``-y:

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

Using Numerical Priorities
--------------------------

Gossip supports specifying *priorities* for registrations. Priorities are numbers (0 by default) by which the call order is determined -- the higher the number, the earlier the registration will be called:

.. code-block:: python
       
       >>> @gossip.register('prioritized', priority=1)
       ... def handler1():
       ...    print('priority 1')
       >>> @gossip.register('prioritized', priority=100)
       ... def handler2():
       ...    print('priority 100')
       >>> @gossip.register('prioritized', priority=-5)
       ... def handler3():
       ...    print('priority -5')
       >>> gossip.trigger('prioritized')
       priority 100
       priority 1
       priority -5

.. note:: Numerical priorities might not behave as expected when mixed with other ordering features, such as needs/provides or signaling



Using Needs/Provides Markers
----------------------------

You can also tackle dependencies at the point of registration, stating that a certain registration needs to happen before or after another registration. The way to do that is stating that the registration *needs* or *provides* something compared to another registration. For example:

.. code-block:: python
       
       >>> @gossip.register("some_hook", needs=["phase1_complete"])
       ... def handler1():
       ...     print("Handler1")

       >>> @gossip.register("some_hook", provides=["phase1_complete"])
       ... def phase1_prepare_something():
       ...     print("Preparing phase 1")

       >>> @gossip.register("some_hook", provides=["phase1_complete"])
       ... def phase1_prepare_another_thing():
       ...     print("Still preparing phase 1")

       >>> gossip.trigger("some_hook")
       Preparing phase 1
       Still preparing phase 1
       Handler1

``needs`` and ``provides`` are mere strings representing a resource or constraint that can be referred to as needed or provided by hook handlers. It merely means that any handler needing a certain thing must be called after the handler providing the thing had fired.

In the above example, the registrations are fired in order to satisfy the needs/provides dependencies. You'll note that multiple handlers can ``provide`` the same thing, which means that all of them must be fired before the handler that ``needs`` that thing.

Dealing with Regular Handlers in Needs/Provides Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Hook handlers that do not specify andy needs/provides constraints, by default, are considered free handlers that can be fired at any point.

In some cases though, you want to make sure those handlers fire only after or before all the constrained handlers are fired. To control this, you should use the :func:`gossip.groups.Group.set_unconstrained_handler_priority`:

.. code-block:: python
       
       >>> @gossip.register('my_group.my_hook')
       ... def dontcare():
       ...     print("I don't care")

       >>> @gossip.register('my_group.my_hook', provides=['something'])
       ... def i_care():
       ...     print("I care!")

       >>> gossip.trigger('my_group.my_hook')
       I don't care
       I care!

       >>> gossip.get_group('my_group').set_unconstrained_handler_priority(gossip.FIRST)
       >>> gossip.trigger('my_group.my_hook')
       I don't care
       I care!

       >>> gossip.get_group('my_group').set_unconstrained_handler_priority(gossip.LAST)
       >>> gossip.trigger('my_group.my_hook')
       I care!
       I don't care




Circular and Unmet Dependencies
-------------------------------

In both approaches to dependency management, Gossip detects dependencies that aren't resolved in time, such as circular dependencies or cases like ``gossip.wait_for(False)``. In such cases, :class:`gossip.exceptions.CannotResolveDependencies` is raised immediately.

