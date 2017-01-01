import itertools

_call_timestamps = itertools.count()


def test_regular_ordering(hook):

    handler1, handler2, handler3 = handlers = [create_handler() for _ in range(3)] # pylint: disable=redefined-builtin

    for h in handlers:
        hook.register(h)

    hook.trigger(kwargs={})

    assert handler1.call_timestamp < handler2.call_timestamp < handler3.call_timestamp

def test_higher_lower_weight(hook):

    lower_priority = create_handler()
    hook.register(lower_priority, priority=-1)

    handler1, handler2, handler3 = handlers = [create_handler() for _ in range(3)] # pylint: disable=redefined-builtin

    higher_priority = create_handler()
    hook.register(higher_priority, priority=1)

    for h in handlers:
        hook.register(h)

    hook.trigger(kwargs={})

    assert handler1.call_timestamp < handler2.call_timestamp < handler3.call_timestamp
    assert lower_priority.call_timestamp > handler3.call_timestamp
    assert higher_priority.call_timestamp < handler1.call_timestamp

def create_handler():
    def returned():
        assert returned.call_timestamp is None
        returned.call_timestamp = next(_call_timestamps)

    returned.call_timestamp = None
    return returned
