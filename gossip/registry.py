import functools

from ._compat import iteritems, itervalues, string_types
from .exceptions import NameAlreadyUsed, HookNotFound
from .group import Group

_hooks = {}

_groups = {
    None: Group("**global**")
}

def define(hook_name):
    """Defines a new hook with the given name

    :returns: The :class:`gossip.hook.Hook` object created
    """
    return create_hook(hook_name)


def register(func, hook_name=None):
    """Registers a new function to a hook

    :param hook_name: full name of hook to register to
    :returns: The function (for decorator chaining)

    """
    if isinstance(func, string_types):
        return functools.partial(register, hook_name=func)
    assert hook_name is not None
    get_or_create_hook(hook_name).register(func)
    return func


def unregister_all(hook_name):
    """
    Unregisters all handlers from the given hook name
    """
    if hook_name in _hooks:
        _hooks[hook_name].unregister_all()


def undefine_all():
    """
    Undefines all defined hooks and groups

    .. attention: this is a dangerous operation - it affects all defined hooks of all namespaces, and should only
      be invoked if nothing else in your program relies on gossip
    """
    _hooks.clear()
    global_group = get_global_group()
    _groups.clear()
    _groups[None] = global_group
    global_group.remove_all_children()

def trigger(hook_name, **kwargs):
    """Triggers a hook by name, causing all of its handlers to be called
    """

    hook = _hooks.get(hook_name)
    if hook is not None:
        hook.trigger(kwargs)


def get_or_create_hook(hook_name):
    try:
        return get_hook(hook_name)
    except HookNotFound:
        return create_hook(hook_name)

def get_hook(hook_name):
    """Gets a hook by its name

    :raises: :class:`gossip.exceptions.HookNotFound` if the hook wasn't defined already
    """
    try:
        return _hooks[hook_name]
    except KeyError:
        raise HookNotFound("Hook {0} does not exist".format(hook_name))


def create_hook(hook_name):
    if hook_name in _hooks:
        raise NameAlreadyUsed(
            "A hook named {0} already exists. Cannot create a hook with the same name".format(hook_name))
    if hook_name in _groups:
        raise NameAlreadyUsed(
            "A group named {0} already exists. Cannot create a hook with the same name".format(hook_name))
    parent = get_global_group()
    group_name = None
    parts = hook_name.split(".")
    for part in parts[:-1]:
        group_name = part if group_name is None else "{0}.{1}".format(
            group_name, part)
        group = _groups.get(group_name)
        if group is None:
            if group_name in _hooks:
                raise NameAlreadyUsed(
                    "A hook named {0} already exists. Cannot create group with the same name".format(group_name))
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
