import gossip
import gossip.groups
import pytest
from gossip.exceptions import NameAlreadyUsed, GroupNotFound, CannotMuteHooks

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

    hook = gossip.get_hook(hook_name)
    hook.register_no_op()

    hook.undefine()
    gossip.define(hook_name)

    assert not gossip.get_hook(hook_name).get_registrations()
    assert not gossip.get_hook(hook_name).get_registrations(include_empty=True)


@pytest.mark.parametrize('include_empty', [True, False])
def test_get_registrations_include_empty(hook_name, include_empty):
    gossip.define(hook_name)

    @gossip.register(hook_name)
    def handler():
        pass

    hook = gossip.get_hook(hook_name)
    hook.register_no_op()

    expected = 2 if include_empty else 1
    assert len(hook.get_registrations(include_empty=include_empty)) == expected


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


def test_mute_group(checkpoint):

    @gossip.register('a.b.c')
    def handler():
        checkpoint()

    gossip.get_group("a").forbid_muting()

    with pytest.raises(CannotMuteHooks):
        with gossip.mute_context(['a.b.c']):
            gossip.trigger('a.b.c')
    assert not checkpoint.called


def test_mute_hook(checkpoint):

    @gossip.register('a.b.c')
    def handler():
        checkpoint()

    hook = gossip.define('a.b.d')
    hook.forbid_muting()
    assert not hook.can_be_muted()

    with gossip.mute_context(['a.b.c']):
        gossip.trigger('a.b.c')
    assert not checkpoint.called


def mute_other_sub_group():
    hook_1 = gossip.define("a.b.c")
    hook_2 = gossip.define("a.c.d")
    hook_3 = gossip.define("a.c.e")

    gossip.get_group("a.b").forbid_muting()
    hook_3.forbid_muting()

    assert not hook_1.can_be_muted()
    assert not hook_3.can_be_muted()
    assert hook_2.can_be_muted()


@pytest.mark.parametrize('params', [])
def test_forbid_muting(params):
    name_for_mute, forbid_name, is_group, is_allowed = params
    getter = gossip.get_group if is_group else gossip.get_hook
    forbidden_obj = getter(forbid_name)
    forbidden_obj.forbid_muting()

    hook = gossip.get_hook(name_for_mute)
    assert hook.can_be_muted() == is_allowed

    forbidden_obj.allow_muting()
    assert hook.can_be_muted() == is_allowed
