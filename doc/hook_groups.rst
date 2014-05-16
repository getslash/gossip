Hook Groups
-----------

Defining and Accessing Groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Gossip aims to fit in environments spanning multiple projects, acting as a communications glue. For this purpose, it may become necessary to handle several hooks as a group, or namespace. Gossip supports this out of the box, and allows you to configure multiple different settings on hook groups.


A *hook group* is automatically formed when you use a dot (``.``) in a hook's name:

.. code-block:: python
		
		>>> import gossip

		>>> @gossip.register("myproject.on_initialize")
		... def handle_initialize():
		...     pass

Groups are implemented as objects (:py:class:`gossip.groups.Group`), and can be easily obtained from the handler:

.. code-block:: python

		>>> obj = handle_initialize.gossip.hook.group
		>>> obj
		<Gossip group 'myproject'>

It can also be accessed globally:

.. code-block:: python

		 >>> gossip.get_group("myproject")
		 <Gossip group 'myproject'>

There's even a shortcut for creating groups explicitly:

.. code-block:: python

		>>> gossip.create_group("new_group")
		<Gossip group 'new_group'>

And getting or creating as necessary:

.. code-block:: python

		>>> gossip.get_or_create_group("new_group")
		<Gossip group 'new_group'>


		

