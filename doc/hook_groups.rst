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

Groups are implemented as objects (:py:class:`gossip.group.Group`), and can be easily obtained from the handler:

.. code-block:: python

		>>> obj = handle_initialize.gossip.hook.group
		>>> obj
		<Gossip group 'myproject'>

It can also be accessed globally:

.. clode-block:: python

		 >>> gossip.get_group_by_name("myproject")
		 <Gossip group 'myproject'>
		
Manipulating Groups
~~~~~~~~~~~~~~~~~~~

*WIP*

Group Settings
~~~~~~~~~~~~~~

*WIP*

