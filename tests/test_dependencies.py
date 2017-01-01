import gossip
import gossip.exceptions
import pytest

from .conftest import RegisteredHook

# pylint: disable=redefined-outer-name


def test_not_now():
    with pytest.raises(gossip.NotNowException):
        gossip.not_now()


def test_wait_for():
    gossip.wait_for(True)
    gossip.wait_for(1)
    gossip.wait_for("string")

    for falsey in [False, "", None, [], ()]:
        with pytest.raises(gossip.NotNowException):
            gossip.wait_for(falsey)


def test_regular_call_order(handlers):
    _trigger(handlers)
    timestamps = [handler.last_timestamp for handler in handlers]
    assert sorted(timestamps) == timestamps


def test_dependency(handlers):
    handlers[3].depend_on(handlers[7])
    _trigger(handlers)
    timestamps = [handler.last_timestamp for handler in handlers]
    assert timestamps != sorted(timestamps)
    timestamps.append(timestamps.pop(3))
    assert timestamps == sorted(timestamps)


def test_circular_dependency(handlers):
    handlers[3].depend_on(handlers[7])
    handlers[7].depend_on(handlers[3])
    with pytest.raises(gossip.exceptions.CannotResolveDependencies):
        _trigger(handlers)
    for index, handler in enumerate(handlers):
        assert handler.called == (index not in (3, 7))


def test_reordering(handlers):  # pylint: disable=redefined-outer-name, unused-argument
    pytest.skip("n/i")


def _trigger(handlers):
    handlers[0].trigger()


@pytest.fixture
def handlers(hook_name):
    return [RegisteredHook(hook_name) for _ in range(10)]
