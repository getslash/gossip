import functools

import gossip
import pytest


def test_token_registration_unregistration():

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

    assert len(gossip.get_all_registrations()) == 4
    gossip.unregister_token("token2")
    assert len(gossip.get_all_registrations()) == 3
    assert not handler4.gossip.is_active()

