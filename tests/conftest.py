import itertools

import gossip
import pytest

hook_id = itertools.count()

@pytest.fixture(autouse=True, scope="function")
def clear_registrations():
    gossip.unregister_all()

@pytest.fixture
def hook_name():
    return "hook{0}".format(next(hook_id))

@pytest.fixture
def registered_hook(hook_name):
    return RegisteredHook(hook_name)

@pytest.fixture
def registered_hooks():
    return [RegisteredHook(hook_name()) for i in range(10)]

class RegisteredHook(object):

    def __init__(self, hook_name):
        super(RegisteredHook, self).__init__()

        self.name = hook_name
        self.kwargs = {"a": 1, "b": 2, "c": 3}
        self.num_called = 0

        gossip.register(func=self.func, hook_name=hook_name)

    def func(self, **kw):
        assert kw == self.kwargs
        self.num_called += 1

    def works(self):
        old_num_caled = self.num_called
        gossip.trigger(self.name, **self.kwargs)
        return self.num_called == old_num_caled + 1
