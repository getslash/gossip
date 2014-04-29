import pytest

from capnhook import Hook

@pytest.mark.parametrize('stringify', [str, repr])
def test_hook_str_repr(stringify):
    assert stringify(Hook("some_name", arg_names=("a", "b"))) == \
        "<Hook some_name(a, b)>"


