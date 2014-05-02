import functools

from ._compat import iteritems, itervalues, string_types
from .exceptions import NameAlreadyUsed
from .group import Group

_hooks = {}

_groups = {
    None: Group("**global**")
}

def register(func, hook_name=None):
    if isinstance(func, string_types):
        return functools.partial(register, hook_name=func)
    assert hook_name is not None
    get_or_create_hook(hook_name).register(func)
    return func

def unregister_all(hook_name=None):
    hook_names = [hook_name] if hook_name is not None else _hooks
    for name in hook_names:
        _hooks[name].unregister_all()

def undefine_all():
    _hooks.clear()
    global_group = get_global_group()
    _groups.clear()
    _groups[None] = global_group
    global_group.remove_all_children()

def trigger(hook_name, **kwargs):
    hook = _hooks.get(hook_name)
    if hook is not None:
        hook.trigger(kwargs)


def get_or_create_hook(hook_name):
    returned = _hooks.get(hook_name)
    if returned is None:
        returned = _hooks[hook_name] = create_hook(hook_name)
    return returned

def create_hook(hook_name):
    if hook_name in _groups:
        raise NameAlreadyUsed("A group named {0} already exists. Cannot create a hook with the same name".format(hook_name))
    parent = get_global_group()
    group_name = None
    parts = hook_name.split(".")
    for part in parts[:-1]:
        group_name = part if group_name is None else "{0}.{1}".format(group_name, part)
        group = _groups.get(group_name)
        if group is None:
            if group_name in _hooks:
                raise NameAlreadyUsed("A hook named {0} already exists. Cannot create group with the same name".format(group_name))
            group = _groups[group_name] = parent.get_or_create_subgroup(part)
        parent = group

    hook = _hooks[hook_name] = parent.create_hook(parts[-1])
    return hook

def get_global_group():
    return _groups[None]

def get_groups():
    return list(group for group_name, group in iteritems(_groups) if group_name is not None)

def get_group_by_name(name):
    return _groups[name]
