import gossip
import gossip.groups
import pytest
from gossip.exceptions import NameAlreadyUsed, GroupNotFound

# pylint: disable=unused-variable

def test_trigger_no_hook_registered():
    result = gossip.trigger("unregistered")  # pylint: disable=assignment-from-no-return
    assert result is None


def test_create_group_twice():
    group_name = "group_name"
    gossip.create_group(group_name)

    with pytest.raises(NameAlreadyUsed):
        gossip.create_group(group_name)


def test_get_or_create_group():
    group_name = "group_name"
    with pytest.raises(GroupNotFound):
        gossip.get_group(group_name)

    group = gossip.get_or_create_group(group_name)
    assert isinstance(group, gossip.groups.Group)
    assert group is gossip.get_group(group_name)


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


def test_undefine(hook_name):
    gossip.define(hook_name)

    @gossip.register(hook_name)
    def handler():
        pass

    gossip.get_hook(hook_name).undefine()
    gossip.define(hook_name)

    assert not gossip.get_hook(hook_name).get_registrations()


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

def test_unregister_all_on_hook(registered_hooks):
    assert all(r.works() for r in registered_hooks)
    gossip.get_hook(registered_hooks[0].name).unregister_all()
    assert not registered_hooks[0].works()
    assert all(r.works() for r in registered_hooks[1:])


def test_global_group_reset_delets_all_group(registered_hooks):
    assert gossip.get_groups()
    gossip.get_global_group().reset()
    assert not gossip.get_groups()
    assert all(not r.works() for r in registered_hooks)
    assert not gossip.get_global_group().get_subgroups()


def test_global_group_is_same(registered_hooks):  # pylint: disable=unused-argument
    global_group = gossip.get_global_group()
    global_group.reset()
    assert gossip.get_global_group() is global_group


def test_hook_name_taken_by_group():
    @gossip.register("group_name.hook")
    def func():
        pass

    with pytest.raises(NameAlreadyUsed):
        @gossip.register("group_name")
        def func2():
            pass

    assert "group_name" not in gossip.registry.hooks


def test_group_name_taken_by_hook():
    @gossip.register("group_name")
    def func():
        pass

    with pytest.raises(NameAlreadyUsed):
        @gossip.register("group_name.hook")
        def func2():
            pass

    assert "group_name" not in gossip.registry.groups


def test_register_class_and_instance_methods():

    class MyClass(object):

        @gossip.register("hook")
        @classmethod
        def class_method(cls):
            pass

        @gossip.register("hook")
        @staticmethod
        def static_method():
            pass

        def regular_method(self):
            pass

    m = MyClass()

    gossip.register("hook")(m.regular_method)


def test_nested_groups():

    @gossip.register("a.b.c")
    def handler():
        pass

    assert gossip.get_group("a").name == "a"
    assert gossip.get_group("a.b").name == "b"


def test_mute_trigger(checkpoint):

    @gossip.register('a.b.c')
    def handler():
        checkpoint()

    with gossip.mute_context(['a.b.c']):
        gossip.trigger('a.b.c')

    assert not checkpoint.called

    gossip.trigger('a.b.c')

    assert checkpoint.called


@pytest.mark.parametrize('arg', ['', 'name', 2, 2.0, True])
def test_mute_accepts_only_lists(arg):

    with pytest.raises(TypeError):
        with gossip.mute_context(arg):
            pass
