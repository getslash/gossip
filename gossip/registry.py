import functools

from ._compat import iteritems, itervalues, string_types
from .exceptions import NameAlreadyUsed, HookNotFound, GroupNotFound
from .group import Group

_hooks = {}

_groups = {
    None: Group("**global**")
}


def define(hook_name, **kwargs):
    """Defines a new hook with the given name

    :returns: The :class:`gossip.hook.Hook` object created
    """
    returned = get_or_create_hook(hook_name, **kwargs)
    if returned.is_defined():
        raise NameAlreadyUsed("Hook {0} is already defined".format(hook_name))
    returned.mark_defined()
    return returned


def register(func=None, hook_name=None, token=None):
    """Registers a new function to a hook

    :param hook_name: full name of hook to register to
    :param token: token to register with. This can be used to later unregister a group of handlers which have a
           specific token
    :returns: The function (for decorator chaining)

    """
    if isinstance(func, string_types):
        assert hook_name is None
        hook_name = func
        func = None

    if func is None:
        return functools.partial(register, hook_name=hook_name, token=token)
    assert hook_name is not None
    registration = get_or_create_hook(hook_name).register(func, token=token)
    assert registration
    return func


def unregister_all(hook_name):
    """
    Unregisters all handlers from the given hook name
    """
    if hook_name in _hooks:
        _hooks[hook_name].unregister_all()


def unregister_token(token):
    """Unregisters all handlers that were registered with ``token``
    """
    # todo: optimize this
    for registration in get_all_registrations():
        if registration.token == token:
            registration.unregister()


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


def get_or_create_hook(hook_name, **kwargs):
    try:
        return get_hook(hook_name)
    except HookNotFound:
        return create_hook(hook_name, **kwargs)


def get_hook(hook_name):
    """Gets a hook by its name

    :raises: :class:`gossip.exceptions.HookNotFound` if the hook wasn't defined already
    """
    try:
        return _hooks[hook_name]
    except KeyError:
        raise HookNotFound("Hook {0} does not exist".format(hook_name))


def create_hook(hook_name, **kwargs):
    if hook_name in _hooks:
        raise NameAlreadyUsed(
            "A hook named {0} already exists. Cannot create a hook with the same name".format(hook_name))
    if hook_name in _groups:
        raise NameAlreadyUsed(
            "A group named {0} already exists. Cannot create a hook with the same name".format(hook_name))

    if "." in hook_name:
        group_name, hook_base_name = hook_name.rsplit(".", 1)
    else:
        group_name = None
        hook_base_name = hook_name

    hook = _hooks[hook_name] = get_or_create_group(
        group_name).create_hook(hook_base_name, **kwargs)
    return hook


def get_global_group():
    return get_group(None)


def get_all_registrations():
    return get_global_group().get_all_registrations()


def get_groups():
    return list(group for group_name, group in iteritems(_groups) if group_name is not None)


def get_group(name):
    """Returns an existing group with a given name

    :raises: KeyError if no such group exists
    """
    try:
        return _groups[name]
    except KeyError:
        raise GroupNotFound(name)


def create_group(name):
    """Creates and returns a new named group

    :rtype: :class:`gossip.group.Group`
    """
    if name in _groups:
        raise NameAlreadyUsed(
            "Group with name {0} already exists".format(name))

    if name in _hooks:
        raise NameAlreadyUsed(
            "Hook with name {0} already exists. Cannot create group with same name".format(name))

    group = get_group(None)

    for part in name.split("."):
        group = group.get_or_create_subgroup(part)

    _groups[name] = group
    return group


def get_or_create_group(name):
    """Tries to retrieve an existing group, and if it doesn't exist, create a new group
    """
    try:
        return get_group(name)
    except GroupNotFound:
        return create_group(name)
