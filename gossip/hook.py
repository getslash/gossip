import logging
import sys

from .exceptions import (CannotResolveDependencies, NotNowException,
                         UndefinedHook)
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
        self._registrations = []
        self._arg_names = arg_names
        self._swallow_exceptions = False
        self._trigger_internal_hooks = self.full_name != "gossip.on_handler_exception"
        self._defined = False
        self.doc = doc

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
            raise UndefinedHook("hook {0} wasn't defined yet".format(self.full_name))
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
                        exc_info = self._call_registration(registration, kwargs)
                    except NotNowException:
                        deferred.append(registration)
                        continue
                    else:
                        any_resolved = True
                    if exc_info is not None:
                        exception_policy.handle_exception(ctx, exc_info)
                if deferred:
                    if not any_resolved:
                        raise CannotResolveDependencies("Cannot resolve handler dependencies")
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
                trigger("gossip.on_handler_exception", handler=registration.func, exception=exc_info)
            _logger.warn("Exception occurred while calling %s",
                         registration, exc_info=exc_info)
            # TODO: debug here
        return exc_info

    def __repr__(self):
        return "<Hook {0}({1})>".format(self.name, ", ".join(self._arg_names))

from .registry import trigger
