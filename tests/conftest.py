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
def handler():
    return Handler()


class Handler(object):

    def __init__(self):
        super(Handler, self).__init__()
        self.num_called = 0

    def __call__(self):
        self.num_called += 1
