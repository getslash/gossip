import functools
import logging
import sys
from contextlib import contextmanager
from types import GeneratorType

from . import groups, registry
from ._compat import itervalues, string_types
from .exceptions import (CannotResolveDependencies, HookNotFound,
                         NameAlreadyUsed, NotNowException, UndefinedHook,
                         UnsupportedHookTags)
from .registration import Registration

_logger = logging.getLogger(__name__)


class Hook(object):

    def __init__(self, group, name, arg_names=(), doc=None):
        super(Hook, self).__init__()
        self.group = group
        self.name = name
        self.tags = None
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

    def set_tags(self, tags):
        assert not self.tags, "Cannot override exists tags {0} with {1}".format(
            self.tags, tags)
        self.tags = tags

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

    def validate_tags(self, tags, is_strict=None):
        if is_strict is None:
            is_strict = self.group.is_strict()
        if not is_strict:
            return
        normalize_tags = lambda tag_: set(tag_) if tag_ is not None else set()
        extra_tags = normalize_tags(tags) - normalize_tags(self.tags)
        if extra_tags:
            raise UnsupportedHookTags("hook {0} support {1} tags, not: {2}".format(
                self.full_name, self.tags, extra_tags))

    def validate_strict(self, registrations_to_validate=None):
        if not self._defined:
            raise UndefinedHook(
                "hook {0} wasn't defined yet".format(self.full_name))
        if registrations_to_validate is None:
            registrations_to_validate = self._registrations
        for registration in registrations_to_validate:
            self.validate_tags(registration.tags, is_strict=True)

    def register(self, func, token=None, tags=None):
        """Registers a new handler to this hook
        """
        returned = Registration(func, self, token=token, tags=tags)
        if self.group.is_strict():
            self.validate_strict([returned])
        self._registrations.append(returned)
        return returned

    def unregister(self, registration):
        assert registration.hook is self
        self._registrations.remove(registration)
        registration.hook = None

    def unregister_all(self):
        del self._registrations[:]

    def trigger(self, kwargs, tags=None):
        if self.full_name in _muted_stack[-1]:
            return

        self.validate_tags(tags)
        exception_policy = self.group.get_exception_policy()

        registrations = self._registrations
        deferred = []

        with exception_policy.context() as ctx:
            while True:
                any_resolved = False
                for registration in registrations:
                    if not registration.has_tags(tags):
                        continue
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
                            "Cannot resolve handler dependencies for {0}".format(self))
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
                        handler=registration.func, exception=exc_info, hook=self)
            _logger.warn("Exception occurred while calling %s",
                         registration, exc_info=exc_info)
            # TODO: debug here
        return exc_info

    def __repr__(self):
        return "<Hook {0}({1})>".format(self.name, ", ".join(self._arg_names))


def trigger(hook_name, **kwargs):
    """Triggers a hook by name, causing all of its handlers to be called
    """
    trigger_with_tags(hook_name, kwargs, None)


def trigger_with_tags(hook_name, kwargs=None, tags=None):
    hook = registry.hooks.get(hook_name)
    if hook is not None:
        hook.trigger(kwargs or {}, tags)


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
    tags = kwargs.pop('tags', None)
    returned = get_or_create_hook(hook_name, **kwargs)
    if returned.is_defined():
        raise NameAlreadyUsed("Hook {0} is already defined".format(hook_name))
    if tags:
        returned.set_tags(tags)
    returned.mark_defined()
    return returned


def register(func=None, hook_name=None, token=None, tags=None):
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
        return functools.partial(register, hook_name=hook_name, token=token, tags=tags)
    assert hook_name is not None
    registration = get_or_create_hook(
        hook_name).register(func, token=token, tags=tags)
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


_muted_stack = [set()]


@contextmanager
def mute_context(hook_names):
    """A context manager, during the execution of which the specified hook names will be ignored. Any code that tries to
    trigger these hooks will trigger no callback.

    :type hook_names: list, tuple or generator of full hook names to mute
    """
    if not isinstance(hook_names, (list, tuple, GeneratorType)):
        raise TypeError('hook names to mute must be a list or a tuple')
    _muted_stack.append(_muted_stack[-1] | set(hook_names))
    try:
        yield
    finally:
        _muted_stack.pop(-1)
