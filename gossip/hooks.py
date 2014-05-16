import functools
import logging
import sys

from . import registry
from . import groups
from ._compat import string_types, itervalues
from .exceptions import (CannotResolveDependencies, HookNotFound,
                         NameAlreadyUsed, NotNowException, UndefinedHook)
from .registration import Registration

_logger = logging.getLogger(__name__)

class Hook(object):

    def __init__(self, group, name, arg_names=(), doc=None):
        super(Hook, self).__init__()
        self.group = group
        self.name = name
        if self.group.is_global():
            self.full_name = name
        else:
            self.full_name = "{0}.{1}".format(self.group.full_name, self.name)
        registry.hooks[self.full_name] = self
        self._registrations = []
        self._arg_names = arg_names
        self._swallow_exceptions = False
        self._trigger_internal_hooks = self.full_name != "gossip.on_handler_exception"
        self._defined = False
        self.doc = doc

    def undefine(self):
        self.group.remove_child(self.name)
        registry.hooks.pop(self.full_name)

    def get_registrations(self):
        return list(self._registrations)

    def mark_defined(self):
        self._defined = True

    def is_defined(self):
        return self._defined

    def get_argument_names(self):
        return self._arg_names

    def __call__(self, **kwargs):
        return self.trigger(kwargs)

    def register(self, func, token=None):
        """Registers a new handler to this hook
        """
        if self.group.is_strict() and not self._defined:
            raise UndefinedHook(
                "hook {0} wasn't defined yet".format(self.full_name))
        returned = Registration(func, self, token=token)
        self._registrations.append(returned)
        return returned

    def unregister(self, registration):
        assert registration.hook is self
        self._registrations.remove(registration)
        registration.hook = None

    def unregister_all(self):
        del self._registrations[:]

    def trigger(self, kwargs):
        exception_policy = self.group.get_exception_policy()

        registrations = self._registrations
        deferred = []

        with exception_policy.context() as ctx:
            while True:
                any_resolved = False
                for registration in registrations:
                    try:
                        exc_info = self._call_registration(
                            registration, kwargs)
                    except NotNowException:
                        deferred.append(registration)
                        continue
                    else:
                        any_resolved = True
                    if exc_info is not None:
                        exception_policy.handle_exception(ctx, exc_info)
                if deferred:
                    if not any_resolved:
                        raise CannotResolveDependencies(
                            "Cannot resolve handler dependencies")
                    registrations = deferred
                    deferred = []
                else:
                    break

    def _call_registration(self, registration, kwargs):
        exc_info = None
        try:
            registration(**kwargs)  # pylint: disable=star-args
        except NotNowException:
            raise
        except:
            exc_info = sys.exc_info()
            if self._trigger_internal_hooks:
                trigger("gossip.on_handler_exception",
                        handler=registration.func, exception=exc_info)
            _logger.warn("Exception occurred while calling %s",
                         registration, exc_info=exc_info)
            # TODO: debug here
        return exc_info

    def __repr__(self):
        return "<Hook {0}({1})>".format(self.name, ", ".join(self._arg_names))


def trigger(hook_name, **kwargs):
    """Triggers a hook by name, causing all of its handlers to be called
    """

    hook = registry.hooks.get(hook_name)
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
        return registry.hooks[hook_name]
    except KeyError:
        raise HookNotFound("Hook {0} does not exist".format(hook_name))

def create_hook(hook_name, **kwargs):
    """Creates a hook with the given full name, creating intermediate groups if necessary
    """
    if hook_name in registry.hooks:
        raise NameAlreadyUsed(
            "A hook named {0} already exists. Cannot create a hook with the same name".format(hook_name))

    if hook_name in registry.groups:
        raise NameAlreadyUsed(
            "A group named {0} already exists. Cannot create a hook with the same name".format(hook_name))

    if "." in hook_name:
        group_name, hook_base_name = hook_name.rsplit(".", 1)
    else:
        group_name = None
        hook_base_name = hook_name

    group = groups.get_or_create_group(group_name)
    hook = Hook(group, hook_base_name, **kwargs)
    group.add_child(hook_base_name, hook)
    return hook


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
    try:
        hook = get_hook(hook_name)
    except HookNotFound:
        return
    hook.unregister_all()


def get_all_hooks():
    return list(itervalues(registry.hooks))
