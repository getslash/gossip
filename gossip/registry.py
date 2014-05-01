import functools

from ._compat import string_types
from .hook import Hook

_hooks = {}

def register(func, hook_name=None):
    if isinstance(func, string_types):
        return functools.partial(register, hook_name=func)
    assert hook_name is not None
    get_or_create_hook(hook_name).register(func)
    return func

def unregister_all():
    _hooks.clear()

def trigger(hook_name, **kwargs):
    hook = _hooks.get(hook_name)
    if hook is not None:
        hook.trigger(kwargs)

def get_or_create_hook(hook_name):
    returned = _hooks.get(hook_name)
    if returned is None:
        returned = _hooks[hook_name] = Hook(hook_name)
    return returned
