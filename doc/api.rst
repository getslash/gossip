API Reference
=============

.. automodule:: gossip

Hook Definition
---------------

.. autofunction:: gossip.define

.. autofunction:: gossip.get_hook

Hook Registration
-----------------

.. autofunction:: gossip.register

Hook Triggering
---------------

.. autofunction:: gossip.trigger

Error Handling
--------------

.. autofunction:: gossip.set_exception_policy

.. autoclass:: gossip.exception_policy.RaiseImmediately

.. autoclass:: gossip.exception_policy.RaiseDefer

.. autoclass:: gossip.exception_policy.IgnoreExceptions

.. autoclass:: gossip.exception_policy.Inherit

Hook Unregistration
-------------------

.. automodule:: gossip.registry

.. autofunction:: gossip.registry.unregister_all

.. autofunction:: gossip.registry.undefine_all

Hook Objects
------------

.. automodule:: gossip.hook

.. autoclass:: gossip.hook.Hook
  :members:

Hook Groups
-----------

.. automodule:: gossip.group

.. autoclass:: gossip.group.Group
  :members:

Exceptions
----------

.. automodule:: gossip.exceptions

.. autoclass:: HookNotFound

.. autoclass:: NameAlreadyUsed
