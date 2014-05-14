from .exception_policy import IgnoreExceptions, RaiseDefer, RaiseImmediately
from .exceptions import NotNowException
from .hook import Hook
from .registry import (create_group, define, get_all_registrations,
                       get_global_group, get_group, get_groups, get_hook,
                       get_or_create_group, register, trigger, unregister_token)


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
