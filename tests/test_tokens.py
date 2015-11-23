import functools

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

    return Munch(handler1=handler1, handler2=handler2, handler3=handler3, handler4=handler4)


def test_token_registration_unregistration(registrations):

    assert len(_get_all_registrations()) == 4
    gossip.unregister_token("token2")
    assert len(_get_all_registrations()) == 3
    assert not registrations.handler4.gossip.is_active()


def test_group_only_token_unregistration(registrations):

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



def _get_all_registrations():
    return [registration for hook in gossip.get_all_hooks() for registration in hook.get_registrations()]
