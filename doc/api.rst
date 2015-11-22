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

.. autofunction:: gossip.trigger_with_tags

Error Handling
--------------

.. autofunction:: gossip.set_exception_policy

.. autoclass:: gossip.exception_policy.RaiseImmediately

.. autoclass:: gossip.exception_policy.RaiseDefer

.. autoclass:: gossip.exception_policy.IgnoreExceptions

.. autoclass:: gossip.exception_policy.Inherit

Hook Dependency
---------------

.. autofunction:: gossip.not_now

.. autofunction:: gossip.wait_for


Hook Unregistration
-------------------

.. autofunction:: gossip.unregister_token

Hook Muting
-----------

.. autofunction:: gossip.mute_context

Hook Objects
------------

.. automodule:: gossip.hooks

.. autoclass:: gossip.hooks.Hook
  :members:

Hook Groups
-----------

.. automodule:: gossip.groups

.. autoclass:: gossip.groups.Group
  :members:

Blueprints
----------

.. autoclass:: gossip.Blueprint
  :members:

Exceptions
----------

.. automodule:: gossip.exceptions

.. autoclass:: HookNotFound

.. autoclass:: NameAlreadyUsed

.. autoclass:: NotNowException

.. autoclass:: CannotResolveDependencies


