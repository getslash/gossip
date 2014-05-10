from .hook import Hook
from .exceptions import NotNowException
from .exception_policy import (
    RaiseDefer, RaiseImmediately, IgnoreExceptions)
from .registry import (get_global_group, get_hook, get_group_by_name, get_groups, define,
                       register, trigger)


def set_exception_policy(policy):
    """This is a shortcut to calling :func:`gossip.group.Group.set_exception_policy` on the global
    hook group"""
    return get_global_group().set_exception_policy(policy)

def not_now():
    """Defers execution of the current handler to later, after other handlers have been called.

    This is useful for depending on other hook handlers
    """
    raise NotNowException()

def wait_for(cond):
    """Defers execution of the current handler (see :func:`not_now`) if ``cond`` is False-y.
    """
    if not cond:
        not_now()
