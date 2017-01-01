from .exception_policy import IgnoreExceptions, RaiseDefer, RaiseImmediately
from .exceptions import NotNowException
from .groups import (create_group, get_global_group, get_group, get_groups,
                     get_or_create_group, unregister_token)
from .hooks import (define, get_all_hooks, get_all_registrations, get_hook, Hook, register, trigger,
                    trigger_with_tags, mute_context
                   )
from .blueprint import Blueprint
from .helpers import FIRST, DONT_CARE, LAST, Toggle


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
