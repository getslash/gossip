import functools

from .hook import Hook

_hooks = {}

def register(hook_name, func=None):
    if func is None:
        return functools.partial(register, hook_name)
    get_or_create_hook(hook_name).register(func)
    return func

def trigger(hook_name, **kwargs):
    hook = _hooks.get(hook_name)
    if hook is not None:
        hook.trigger(kwargs)

def get_or_create_hook(hook_name):
    returned = _hooks.get(hook_name)
    if returned is None:
        returned = _hooks[hook_name] = Hook(hook_name)
    return returned
