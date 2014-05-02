import pytest

from gossip import Hook, get_global_group

@pytest.mark.parametrize('stringify', [str, repr])
def test_hook_str_repr(stringify):
    assert stringify(Hook(get_global_group(), "some_name", arg_names=("a", "b"))) == \
        "<Hook some_name(a, b)>"


