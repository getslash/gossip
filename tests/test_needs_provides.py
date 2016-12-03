import pytest

import gossip
from gossip.exceptions import CannotResolveDependencies


def test_needs_provides_simple(timeline):
    evt1 = timeline.register(needs=['something'])
    evt2 = timeline.register(provides=['something'])
    timeline.trigger()
    assert evt1.timestamp > evt2.timestamp


def test_unmet_deps_after_unregister(hook, counter):
    reg = hook.register(counter.plus_one, provides=['something'])
    hook.register(counter.plus_one, needs=['something'])

    reg.unregister()
    with pytest.raises(CannotResolveDependencies):
        hook.trigger({})
    assert counter.get() == 0


def test_unmet_deps_resolved_after_unregister_all(hook, counter):
    hook.register(counter.plus_one, needs=['1'])
    hook.register(counter.plus_one, needs=['2'])
    hook.register_no_op(provides=['3'])
    assert len(hook._registrations) == 2  # pylint: disable=protected-access
    assert len(hook._empty_regisrations) == 1  # pylint: disable=protected-access
    assert len(hook._unmet_deps) == 2  # pylint: disable=protected-access

    hook.unregister_all()
    assert len(hook._registrations) == 0  # pylint: disable=protected-access
    assert len(hook._empty_regisrations) == 0  # pylint: disable=protected-access
    assert len(hook._unmet_deps) == 0  # pylint: disable=protected-access

    hook.trigger({})
    assert counter.get() == 0


def test_needs_provides_complex(timeline):
    events = [
        timeline.register(provides=['0'], needs=['1']),
        timeline.register(provides=['1'], needs=['2', '3']),
        timeline.register(provides=['2'], needs=['5']),
        timeline.register(provides=['3'], needs=['5']),
        timeline.register(provides=['4'], needs=['0']),
        timeline.register(provides=['5']),
    ]
    timeline.trigger()

    assert sorted(events, key=lambda e: e.timestamp) == [
        events[5], events[3], events[2], events[1], events[0], events[4]
    ]


def test_needs_provides_cyclic_simple(timeline):
    timeline.register(needs=['1'], provides=['0'])
    with pytest.raises(CannotResolveDependencies):
        timeline.register(needs=['0'], provides=['1'])
    # make sure the cyclic registration was not added
    assert len(gossip.get_hook(timeline.hook_name)._registrations) == 1  # pylint: disable=protected-access


def test_needs_provides_cyclic_complex(timeline):
    timeline.register(needs=['1'], provides=['0'])
    timeline.register(needs=['2'], provides=['1'])
    timeline.register(needs=['3'], provides=['2'])
    timeline.register(needs=['4'], provides=['3'])
    with pytest.raises(CannotResolveDependencies):
        timeline.register(needs=['0'], provides=['4'])
    # make sure the cyclic registration was not added
    assert len(gossip.get_hook(timeline.hook_name)._registrations) == 4  # pylint: disable=protected-access


def test_register_no_op_does_not_allow_needs_parameter(hook):
    with pytest.raises(NotImplementedError):
        hook.register_no_op(needs=['something'])
    assert len(hook._unmet_deps) == 0  # pylint: disable=protected-access


def test_register_no_op_solves_dependencies(timeline):
    timeline.register(needs=['1'], provides=['0'])
    timeline.register(needs=['2'], provides=['1'])
    assert len(gossip.get_hook(timeline.hook_name)._registrations) == 2  # pylint: disable=protected-access

    with pytest.raises(CannotResolveDependencies):
        timeline.trigger()

    timeline.get_hook().register_no_op(provides=['2'])
    # Make sure "register_no_op" is not registred as "regular" callback
    assert len(gossip.get_hook(timeline.hook_name)._registrations) == 2  # pylint: disable=protected-access
    assert len(gossip.get_hook(timeline.hook_name)._empty_regisrations) == 1  # pylint: disable=protected-access

    timeline.trigger()


def test_unregister_no_op_remove_dependencies(timeline):
    timeline.register(needs=['1'], provides=['0'])
    timeline.register(needs=['2'], provides=['1'])

    hook = timeline.get_hook()
    registration = hook.register_no_op(provides=['2'])
    timeline.trigger()

    registration.unregister()
    with pytest.raises(CannotResolveDependencies):
        gossip.trigger(hook.full_name)


@pytest.mark.parametrize('priority', [gossip.FIRST, gossip.DONT_CARE, gossip.LAST])
@pytest.mark.parametrize('use_parent_group', [True, False])
def test_needs_provides_unconstrained_priority(timeline, priority, use_parent_group):
    dontcare = timeline.register()
    evt1 = timeline.register(needs=['a'], provides=['b'])
    evt2 = timeline.register(provides=['a'])
    if use_parent_group:
        group = timeline.get_parent_group()
    else:
        group = timeline.get_group()

    group.set_unconstrained_handler_priority(priority)
    timeline.trigger()

    if priority in (gossip.FIRST, gossip.DONT_CARE):
        assert dontcare.timestamp < evt2.timestamp < evt1.timestamp
    else:
        assert evt2.timestamp < evt1.timestamp < dontcare.timestamp


def test_policy_gets_reset():
    gossip.get_global_group().set_unconstrained_handler_priority(gossip.FIRST)
    gossip.get_global_group().reset()
    assert gossip.get_global_group().get_unconstrained_handler_priority() == gossip.DONT_CARE


def test_unmet_dependencies(timeline):
    # pylint: disable=unused-variable
    evt = timeline.register(needs=['a'])
    with pytest.raises(CannotResolveDependencies):
        timeline.trigger()

    evt2 = timeline.register(provides=['a'])
    timeline.trigger() # ok
