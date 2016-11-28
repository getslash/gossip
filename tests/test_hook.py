import pytest

from gossip import Hook, get_global_group, define, trigger, register


def test_pre_trigger_callback(checkpoint):
    called_args = []

    hook = define('somehook')

    @hook.add_pre_trigger_callback
    def pre_trigger_callback(registration, kwargs):  # pylint: disable=unused-variable
        called_args.append((registration, kwargs))

    assert not called_args

    trigger('somehook')

    assert not called_args

    @register('somehook')
    def callback(**kwargs):  # pylint: disable=unused-argument
        checkpoint()

    assert not called_args

    trigger('somehook', x=1, y=2, z=3)

    assert len(called_args) == 1
    assert called_args[0][-1] == {'x': 1, 'y': 2, 'z': 3}
    assert called_args[0][0].func is callback


def test_remove_pre_trigger_callback():
    # pylint: disable=protected-access
    hook = define('hook')

    @hook.add_pre_trigger_callback
    def callback():
        pass

    assert len(hook._pre_trigger_callbacks) == 1
    hook.remove_pre_trigger_callback(callback)
    assert not hook._pre_trigger_callbacks


@pytest.mark.parametrize('stringify', [str, repr])
def test_hook_str_repr(stringify):
    assert stringify(Hook(get_global_group(), "some_name", arg_names=("a", "b"))) == \
        "<Hook some_name(a, b)>"
