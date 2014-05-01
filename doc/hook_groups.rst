Hook Groups
-----------

Gossip aims to fit in environments spanning multiple projects, acting as a communications glue. For this purpose, it may become necessary to handle several hooks as a group, or namespace. Gossip supports this out of the box, and allows you to configure multiple different settings on hook groups.


A *hook group* is automatically formed when you use a dot (``.``) in hook's name:

.. code-block:: python
		
		>>> import gossip

		>>> @gossip.register("myproject.on_initialize")
		... def handle_initialize():
		...     pass

