import gossip
from gossip import registry as gossip_registry
import pytest
from gossip.exceptions import NameAlreadyUsed

def test_hook_documentation():
    docstring = "fdkjfkdjfd"
    gossip.define("some_hook", doc=docstring)
    assert gossip.get_hook("some_hook").doc == docstring

def test_register_trigger(registered_hook):
    assert registered_hook.works()

def test_define_twice(hook_name):
    gossip.define(hook_name)
    with pytest.raises(NameAlreadyUsed):
        gossip.define(hook_name)

def test_get_hook(hook_name):
    with pytest.raises(LookupError):
        gossip.get_hook(hook_name)
    hook = gossip.define(hook_name)
    assert gossip.get_hook(hook_name) is hook

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

def test_unregister_group():
    gossip.register("group.a")(lambda: None)
    gossip.register("group.b")(lambda: None)
    gossip.register("group.subgroup.a")(lambda: None)

    group = gossip.get_group("group")
    assert all(hook.get_registrations() for hook in group.get_all_hooks())
    group.unregister_all()
    assert all(not hook.get_registrations() for hook in group.get_all_hooks())


def test_unregister_all_on_hook(registered_hooks):
    assert all(r.works() for r in registered_hooks)
    gossip_registry.unregister_all(registered_hooks[0].name)
    assert not registered_hooks[0].works()
    assert all(r.works() for r in registered_hooks[1:])

def test_unregister_all_does_not_deletes_group(registered_hooks):
    assert gossip.get_groups()
    for h in registered_hooks:
        gossip_registry.unregister_all(h.name)
    assert gossip.get_groups()

def test_undefine_all_deletes_groups(registered_hooks):
    assert gossip.get_groups()
    gossip_registry.undefine_all()
    assert not gossip.get_groups()
    assert all(not r.works() for r in registered_hooks)
    assert not gossip.get_global_group().get_subgroups()

def test_global_group_is_same(registered_hooks):
    global_group = gossip.get_global_group()
    gossip_registry.undefine_all()
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
