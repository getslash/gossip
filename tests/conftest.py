import itertools

import gossip
import gossip.hooks
import pytest

hook_id = itertools.count()

@pytest.fixture(autouse=True, scope="function")
def clear_registrations():
    for hook in gossip.get_all_hooks():
        hook.unregister_all()

@pytest.fixture(autouse=True, scope="function")
def undefine_all():
    gossip.get_global_group().reset()

@pytest.fixture
def hook_name():
    return "hook{0}".format(next(hook_id))

@pytest.fixture
def hook(hook_name):
    return gossip.define(hook_name)

@pytest.fixture
def registered_hook(hook_name):
    return RegisteredHook(hook_name)

@pytest.fixture
def registered_hooks():
    returned = []
    for i in range(10):
        if i % 3 == 0:
            hook_name = "group{0}.hook{1}".format(next(hook_id), next(hook_id))
        else:
            hook_name = "hook{0}".format(next(hook_id))
        returned.append(RegisteredHook(hook_name))
    return returned

timestamp = itertools.count()

class RegisteredHook(object):

    def __init__(self, hook_name):
        super(RegisteredHook, self).__init__()

        self.name = hook_name
        self._fail = False
        self.kwargs = {"a": 1, "b": 2, "c": 3}
        self.num_called = 0
        self._dependency = None

        class HandlerException(Exception):
            pass

        self.exception_class = HandlerException

        def handler(**kw):
            assert kw == self.kwargs
            gossip.wait_for(self._dependency is None or self._dependency.called)
            if self._dependency is not None:
                assert self._dependency.called
            self.num_called += 1
            self.last_timestamp = next(timestamp)
            if self._fail:
                raise self.exception_class()

        self.func = handler

        gossip.register(func=handler, hook_name=hook_name)

    def depend_on(self, hook):
        self._dependency = hook

    @property
    def called(self):
        return self.num_called > 0

    def fail_when_called(self):
        self._fail = True

    def works(self):
        old_num_caled = self.num_called
        self.trigger()
        return self.num_called == old_num_caled + 1

    def trigger(self):
        gossip.trigger(self.name, **self.kwargs)



@pytest.fixture
def checkpoint():
    return Checkpoint()


class Checkpoint(object):

    called = False

    def __call__(self):
        self.called = True
