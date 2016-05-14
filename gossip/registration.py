import itertools
import sys
import types
from contextlib import contextmanager

from ._compat import string_types

PY26 = sys.version_info < (2, 7)

_registration_id = itertools.count()

_token_registrations = {}


class Registration(object):

    def __init__(self, func, hook, token=None, tags=None, needs=None, provides=None, reentrant=True, toggles_on=None, toggles_off=None):
        super(Registration, self).__init__()

        assert not (toggles_off is not None and toggles_on is not None), 'Cannot specify both toggles_on and toggles_off'
        self.id = next(_registration_id)
        self.hook = hook
        self.func = func
        self.token = token
        self.needs = _normalize_deps(needs)
        self.provides = _normalize_deps(provides)
        self.reentrant = reentrant
        self._is_being_called = False
        self.tags = set(tags) if tags else None
        if not isinstance(func, (classmethod, staticmethod, types.MethodType)) and not hasattr(func, "gossip"):
            func.gossip = self

        self.valid = True
        self._toggles_on = toggles_on
        self._toggles_off = toggles_off

    def invalidate(self):
        self.valid = False

    def has_tags(self, tags):
        if tags is None:
            return True
        if self.tags is None:
            return True
        return bool(set(tags) & self.tags)

    def unregister(self):
        if self.hook is not None:
            self.hook.unregister(self)
            assert self.hook is None

    def is_active(self):
        return self.hook is not None

    def is_being_called(self):
        return self._is_being_called

    def can_be_called(self):
        return True

    def __call__(self, *args, **kwargs):
        assert self.valid

        if not self._check_toggle():
            return

        prev = self._is_being_called
        try:
            self._is_being_called = True
            return self.func(*args, **kwargs)
        finally:
            self._is_being_called = prev

    def _check_toggle(self):

        if self._toggles_on is not None:
            if self._toggles_on.is_on():
                return False
            self._toggles_on.toggle()

        if self._toggles_off is not None:
            if self._toggles_off.is_off():
                return False
            self._toggles_off.toggle()

        return True

    def __repr__(self):
        return repr(self.func)


def _normalize_deps(deps):
    if not deps:
        deps = ()
    if isinstance(deps, string_types):
        deps = [deps]
    return frozenset(deps)
