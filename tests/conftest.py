import itertools
from uuid import uuid4

import logbook
import gossip
import gossip.hooks
import pytest

hook_id = itertools.count()


@pytest.fixture(autouse=True, scope='session')
def setup_logging():
    logbook.StderrHandler().push_application()
    logbook.Flags(errors='raise').push_application()

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
def token():
    return str(uuid4())


@pytest.fixture
def checkpoint():
    return Checkpoint()


class Checkpoint(object):

    num_times = 0

    def __call__(self):
        self.num_times += 1

    @property
    def called(self):
        return self.num_times > 0

    def reset(self):
        self.num_times = 0


class Timeline(object):

    def __init__(self):
        super(Timeline, self).__init__()
        self.hook_name = 'parent_group_{0}.subgroup_{0}.hook_{1}'.format(uuid4(), uuid4())
        self.timestamps = itertools.count(1000)
        self.event_index = itertools.count()

    def get_group(self):
        return gossip.get_group(self.hook_name.rsplit('.', 1)[0])

    def get_parent_group(self):
        return gossip.get_group(self.hook_name.split('.')[0])

    def register(self, **kwargs):
        evt = Event(next(self.event_index))
        @gossip.register(self.hook_name, **kwargs)
        def callback():
            evt.timestamp = next(self.timestamps)
        return evt

    def trigger(self):
        gossip.trigger(self.hook_name)

@pytest.fixture
def timeline():
    return Timeline()

class Event(object):

    _timestamp = None

    def __init__(self, index):
        super(Event, self).__init__()
        self.index = index

    def __repr__(self):
        return '<Evt {0}>'.format(self.index)

    @property
    def timestamp(self):
        assert self._timestamp is not None
        return self._timestamp

    @timestamp.setter
    def timestamp(self, t):
        assert self._timestamp is None
        self._timestamp = t


class Counter(object):

    _value = 0

    def set(self, value):
        self._value = value

    def __nonzero__(self):
        return bool(self._value)

    def __bool__(self):
        return bool(self._value)

    def __iadd__(self, i):
        self._value += i

    add = __iadd__

    def __isub__(self, i):
        self._value -= i

    sub = __isub__

    def __eq__(self, other):
        return self._value == other

    def __ne__(self, other):
        return not (self == other) # pylint: disable=superfluous-parens

    def get(self):
        return self._value

    value = property(get)

@pytest.fixture
def counter():
    return Counter()

@pytest.fixture
def counter2():
    return Counter()
