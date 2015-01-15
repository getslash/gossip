import sys
import itertools
import types

PY26 = sys.version_info < (2, 7)

_registration_id = itertools.count()

_token_registrations = {}


class Registration(object):

    def __init__(self, func, hook, token=None, tags=None):
        super(Registration, self).__init__()
        self.id = next(_registration_id)
        self.hook = hook
        self.func = func
        self.token = token
        self.tags = set(tags) if tags else None
        if not isinstance(func, (classmethod, staticmethod, types.MethodType)) and not hasattr(func, "gossip"):
            func.gossip = self

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
        return self.func(*args, **kwargs)

    def __repr__(self):
        return repr(self.func)
