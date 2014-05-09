from .hook import Hook
from .exception_policy import (
    RaiseDefer, RaiseImmediately, IgnoreExceptions)
from .registry import (get_global_group, get_hook, get_group_by_name, get_groups, define,
                       register, trigger)


def set_exception_policy(policy):
    """This is a shortcut to calling :func:`gossip.group.Group.set_exception_policy` on the global
    hook group"""
    return get_global_group().set_exception_policy(policy)
