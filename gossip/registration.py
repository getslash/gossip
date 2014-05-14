import itertools

_registration_id = itertools.count()

_token_registrations = {}


class Registration(object):

    def __init__(self, func, hook, token=None):
        super(Registration, self).__init__()
        self.id = next(_registration_id)
        self.hook = hook
        self.func = func
        self.token = token
        if not hasattr(self.func, "gossip"):
            self.func.gossip = self

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
