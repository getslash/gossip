import gossip
import pytest
from gossip.exceptions import NameAlreadyUsed


def test_register_trigger(registered_hook):
    assert registered_hook.works()

def test_register_function_already_has_gossip_attr(hook_name):
    def func():
        pass

    func.gossip = old_obj = object()

    gossip.register(func=func, hook_name=hook_name)
    assert func.gossip is old_obj

def test_unregister(registered_hook):
    assert registered_hook.works()
    registered_hook.func.gossip.unregister()
    assert not registered_hook.works()

def test_unregister_all(registered_hooks):
    assert all(r.works() for r in registered_hooks)
    gossip.unregister_all()
    assert all(not r.works() for r in registered_hooks)

def test_unregister_all_specific(registered_hooks):
    assert all(r.works() for r in registered_hooks)
    gossip.unregister_all(registered_hooks[0].name)
    assert not registered_hooks[0].works()
    assert all(r.works() for r in registered_hooks[1:])

def test_unregister_all_does_not_deletes_group(registered_hooks):
    assert gossip.get_groups()
    gossip.unregister_all()
    assert gossip.get_groups()

def test_undefine_all_deletes_groups(registered_hooks):
    assert gossip.get_groups()
    gossip.undefine_all()
    assert not gossip.get_groups()
    assert all(not r.works() for r in registered_hooks)

def test_global_group_is_same(registered_hooks):
    global_group = gossip.get_global_group()
    gossip.unregister_all()
    assert gossip.get_global_group() is global_group

def test_hook_name_taken_by_group():
    @gossip.register("group_name.hook")
    def func():
        pass

    with pytest.raises(NameAlreadyUsed):
        @gossip.register("group_name")
        def func2():
            pass

    assert "group_name" not in gossip.registry._hooks

def test_group_name_taken_by_hook():
    @gossip.register("group_name")
    def func():
        pass

    with pytest.raises(NameAlreadyUsed):
        @gossip.register("group_name.hook")
        def func2():
            pass

    assert "group_name" not in gossip.registry._groups
