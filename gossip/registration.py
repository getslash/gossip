import sys
import itertools
import types

from ._compat import string_types

PY26 = sys.version_info < (2, 7)

_registration_id = itertools.count()

_token_registrations = {}


class Registration(object):

    def __init__(self, func, hook, token=None, tags=None, needs=None, provides=None):
        super(Registration, self).__init__()
        self.id = next(_registration_id)
        self.hook = hook
        self.func = func
        self.token = token
        self.needs = _normalize_deps(needs)
        self.provides = _normalize_deps(provides)
        self.tags = set(tags) if tags else None
        if not isinstance(func, (classmethod, staticmethod, types.MethodType)) and not hasattr(func, "gossip"):
            func.gossip = self

        self.valid = True

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

    def can_be_called(self):
        return True

    def __call__(self, *args, **kwargs):
        assert self.valid
        return self.func(*args, **kwargs)

    def __repr__(self):
        return repr(self.func)


def _normalize_deps(deps):
    if not deps:
        deps = ()
    if isinstance(deps, string_types):
        deps = [deps]
    return frozenset(deps)
