from munch import Munch

import gossip
import pytest


def test_prevent_recursive_calls(registered_hook):
    registered_hook.fail_when_called()
    called = Munch(count=0)

    @gossip.register("gossip.on_handler_exception")
    def handle_exception(handler, exception):
        called.count += 1
        raise CustomException()

    with pytest.raises(CustomException):
        registered_hook.trigger()

    assert called.count == 1

class CustomException(Exception):
    pass

def test_gossip_exception_caught_hook(registered_hook):
    registered_hook.fail_when_called()
    error = Munch(caught=False)
    @gossip.register("gossip.on_handler_exception")
    def handle_exception(handler, exception):
        assert handler is registered_hook.func
        assert exception[0] is registered_hook.exception_class
        assert isinstance(exception[1], registered_hook.exception_class)
        error.caught = True


    with pytest.raises(registered_hook.exception_class):
        registered_hook.trigger()

    assert error.caught
