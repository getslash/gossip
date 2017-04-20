from munch import Munch

import gossip
import pytest


@pytest.fixture
def registrations():
    @gossip.register("group.hook1")
    def handler1():
        pass

    @gossip.register("group.hook2", token="token1")
    def handler2():
        pass

    @gossip.register("group2.subgroup.hook3", token="token1")
    def handler3():
        pass

    @gossip.register("group3.subgroup.subgroup2.hook4", token="token2")
    def handler4():
        pass

    handler_no_op = gossip.get_hook("group3.subgroup.subgroup2.hook4").register_no_op(token="token1")

    return Munch(handler1=handler1, handler2=handler2, handler3=handler3, handler4=handler4,
                 handler_no_op=handler_no_op)


def test_token_registration_unregistration(registrations):

    assert len(_get_all_registrations()) == 4
    gossip.unregister_token("token2")
    assert len(_get_all_registrations()) == 3
    assert not registrations.handler4.gossip.is_active()


def test_group_only_token_unregistration(registrations):  # pylint: disable=unused-argument

    gossip.get_group("group2").unregister_token("token1")
    assert len(_get_all_registrations()) == 3


def test_token_unregister_from_hook(checkpoint, token, hook_name):
    # pylint: disable=unused-variable

    @gossip.register(hook_name, token=token)
    def handler():
        gossip.unregister_token(token)
    gossip.register(hook_name)(checkpoint)

    gossip.trigger(hook_name)
    assert checkpoint.called


def test_unregister_token_include_empty(registrations):
    assert len(_get_all_registrations()) == 4
    assert len(_get_all_registrations(include_empty=True)) == 5

    gossip.unregister_token('token1')
    assert len(_get_all_registrations()) == 2
    assert not registrations.handler_no_op.is_active()


def test_token_unregister_from_hook_multiple_token_registrants(checkpoint, token, hook_name):
    # pylint: disable=unused-variable

    @gossip.register(hook_name, token=token)
    def handler():
        gossip.unregister_token(token)
    gossip.register(hook_name)(checkpoint)
    # the second token registration should not be called!
    gossip.register(hook_name, token=token)(checkpoint)

    gossip.trigger(hook_name)
    assert checkpoint.num_times == 1


def _get_all_registrations(include_empty=False):
    return [registration
            for hook in gossip.get_all_hooks()
            for registration in hook.get_registrations(include_empty=include_empty)]
