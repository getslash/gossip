import gossip
import gossip.group
from gossip.exceptions import GroupNotFound, NameAlreadyUsed
import pytest


def test_trigger_no_hook_registered():
    result = gossip.trigger("unregistered")
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
    assert isinstance(group, gossip.group.Group)
    assert group is gossip.get_group(group_name)
