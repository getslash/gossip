import functools
import logbook
import sys
from collections import OrderedDict
from contextlib import contextmanager
from types import GeneratorType
from sentinels import Sentinel

from . import groups, registry
from ._compat import itervalues, string_types
from .exceptions import (CannotResolveDependencies, HookNotFound,
                         NameAlreadyUsed, NotNowException, UndefinedHook,
                         UnsupportedHookTags)
from .registration import Registration
from .utils import topological_sort_registrations

from vintage import warn_deprecation

_logger = logbook.Logger(__name__)

_REGISTER_NO_OP = Sentinel('REGISTER_NO_OP')


class Hook(object):

    def __init__(self, group, name, arg_names=None, doc=None, deprecated=False):
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
        self._empty_regisrations = []
        self._arguments = self._normalize_arguments(arg_names)
        self._trigger_internal_hooks = self.full_name != "gossip.on_handler_exception"
        self._defined = False
        self._pre_trigger_callbacks = []
        self._unmet_deps = frozenset()
        self.doc = doc
        self.deprecated = deprecated

    def _get_registration_list_from_func(self, func):
        if func is _REGISTER_NO_OP:
            return self._empty_regisrations
        return self._registrations

    def _normalize_arguments(self, arg_names):
        if arg_names is None:
            return None

        if isinstance(arg_names, dict):
            return OrderedDict(arg_names)

        return OrderedDict((arg_name, None) for arg_name in arg_names)

    def add_pre_trigger_callback(self, callback):
        self._pre_trigger_callbacks.append(callback)
        return callback

    def remove_pre_trigger_callback(self, callback):
        self._pre_trigger_callbacks.remove(callback)

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
        return tuple(self._arguments)

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

    def validate_kwargs(self, kwargs):
        if self._arguments is None or not self.group.is_strict():
            return

        unknown = set(kwargs) - set(self._arguments)
        if unknown:
            raise TypeError('Unknown arguments specified: {}'.format(', '.join(unknown)))

        for arg_name, arg_types in self._arguments.items():
            if arg_name not in kwargs:
                raise TypeError('Missing argument {!r}'.format(arg_name))
            if arg_types is not None and not isinstance(kwargs[arg_name], arg_types):
                raise TypeError('Incorrect type for argument {}. Expected {!r}, got {!r}'.format(
                    arg_name, arg_types, type(kwargs[arg_name])))


    def validate_strict(self, registrations_to_validate=None):
        if not self._defined:
            raise UndefinedHook(
                "hook {0} wasn't defined yet".format(self.full_name))
        if registrations_to_validate is None:
            registrations_to_validate = self._registrations + self._empty_regisrations
        for registration in registrations_to_validate:
            self.validate_tags(registration.tags, is_strict=True)

    def register(self, func, token=None, tags=None, needs=None, provides=None, **kwargs):
        """Registers a new handler to this hook
        """
        if self.deprecated:
            warn_deprecation('Hook {0} is deprecated!'.format(self.full_name), frame_correction=+1)
        new_registration = Registration(func, self, token=token, tags=tags, needs=needs, provides=provides, **kwargs)
        if self.group.is_strict():
            self.validate_strict([new_registration])
        need_sorting = self._registrations and new_registration.priority > self._registrations[-1].priority
        self._get_registration_list_from_func(func).append(new_registration)
        if need_sorting:
            self._registrations.sort(key=Registration.get_priority, reverse=True) # sort is stable, so order among registration isn't disturbed
        if new_registration.needs or new_registration.provides:
            try:
                self.recompute_call_order()
            except:
                self._registrations.pop()
                raise
        return new_registration

    def register_no_op(self, **kwargs):
        if kwargs.get('needs'):
            raise NotImplementedError("Cannot define 'needs' for register_no_op")
        return self.register(func=_REGISTER_NO_OP, **kwargs)

    def recompute_call_order(self):
        self._registrations = topological_sort_registrations(self._registrations, unconstrained_priority=self.group.get_unconstrained_handler_priority())
        self._unmet_deps = frozenset(n for r in self._registrations for n in r.needs) - \
                           frozenset(p for r in (self._registrations + self._empty_regisrations) for p in r.provides)


    def unregister(self, registration):
        assert registration.hook is self
        self._get_registration_list_from_func(registration.func).remove(registration)
        registration.hook = None
        self.recompute_call_order()

    def unregister_all(self):
        del self._registrations[:]
        del self._empty_regisrations[:]
        self.recompute_call_order()

    def trigger(self, kwargs, tags=None):
        if self._unmet_deps:
            deps_str = ', '.join([str(dep) for dep in self._unmet_deps])
            raise CannotResolveDependencies('Hook {0!r} has unmet dependencies: {1}'.format(self, deps_str))
        if self.full_name in _muted_stack[-1]:
            _logger.debug("Hook {0!r} muted, skipping trigger", self)
            return

        self.validate_tags(tags)
        self.validate_kwargs(kwargs)
        exception_policy = self.group.get_exception_policy()

        registrations = self._registrations
        deferred = []

        with exception_policy.context() as ctx:
            while True:
                any_resolved = False
                for registration in list(registrations):
                    if not registration.valid:
                        continue
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
        if registration.is_being_called() and not registration.reentrant:
            return
        exc_info = None
        for callback in self._pre_trigger_callbacks:
            callback(registration, kwargs)
        try:
            registration(**kwargs)
        except NotNowException:
            raise
        except Exception:  # pylint: disable=broad-except
            exc_info = sys.exc_info()
            if self._trigger_internal_hooks:
                trigger("gossip.on_handler_exception",
                        handler=registration.func, exception=exc_info, hook=self)
            _logger.debug("Exception occurred while calling {0}", registration, exc_info=exc_info)
        return exc_info

    def __repr__(self):
        return "<Hook {0}({1})>".format(self.name, ", ".join(self._arguments or ()))


def trigger(hook_name, **kwargs):
    """Triggers a hook by name, causing all of its handlers to be called
    """
    trigger_with_tags(hook_name, kwargs, None)


def trigger_with_tags(hook_name, kwargs=None, tags=None):
    """Triggers a hook by name, specifying the tags to use when triggering.
    If the hook receives keyword arguments, they have to be passed using the *kwargs* parameter, and not via
    direct keyword arguments
    """
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


def register(func=None, hook_name=None, token=None, tags=None, needs=None, provides=None, reentrant=True, toggles_on=None, toggles_off=None, priority=0):
    """Registers a new function to a hook

    :param hook_name: full name of hook to register to
    :param token: token to register with. This can be used to later unregister a group of handlers which have a
           specific token
    :param needs: list of keywords (strings) that this registration needs, causing any hook that provides any of them to happen before this registration
    :param provides: list of keywords (strings) that this registration provides
    :param reentrent: specifies whether this hook can reenter (i.e. be called in recursion)
    :param toggles_on: specifies a toggle object to turn on when calling this registration. The registration will not be called if the toggle isn't off
    :param toggles_off: specifies a toggle object to turn off when calling this registration. The registration will not be called if the toggle isn't on
    :returns: The function (for decorator chaining)

    """
    if isinstance(func, string_types):
        assert hook_name is None
        hook_name = func
        func = None

    if func is None:
        return functools.partial(
            register,
            hook_name=hook_name,
            token=token,
            tags=tags,
            needs=needs,
            provides=provides,
            reentrant=reentrant,
            toggles_on=toggles_on,
            toggles_off=toggles_off,
            priority=priority,
        )
    assert hook_name is not None
    registration = get_or_create_hook(
        hook_name).register(
            func, token=token, tags=tags, needs=needs, provides=provides, reentrant=reentrant,
            toggles_on=toggles_on, toggles_off=toggles_off,
            priority=priority,
        )
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

def get_all_registrations():
    return [reg for hook in get_all_hooks()
            for reg in hook.get_registrations()]


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
