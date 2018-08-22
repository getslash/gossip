import pytest

from gossip import Hook, get_global_group, define, trigger, register
from gossip.exceptions import UnsupportedHookParams


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


def test_register_hook_before_defining(doc_string):
    @register('hook_a')
    def hook_a_registration(**_):  # pylint: disable=unused-variable
        pass

    tags = ('my', 'tags')
    hook_a = define('hook_a', tags=tags, arg_names=('x', 'y'), deprecated=True, doc=doc_string, can_be_muted=False)
    hook_b = define('hook_b', tags=tags, arg_names=('z', 'y'), deprecated=True, doc=doc_string, can_be_muted=False)

    @register('hook_b')
    def hook_b_registration(**_):  # pylint: disable=unused-variable
        pass

    for hook in (hook_a, hook_b):
        assert hook.tags == tags
        assert hook.doc == doc_string
        assert not hook.can_be_muted()
        assert hook.deprecated
    assert hook_a.get_argument_names() == ('x', 'y')
    assert hook_b.get_argument_names() == ('z', 'y')


def test_unsupported_hook_params():
    unsupported_params = {'unkown_param_a': 1, 'unkown_param_b': 2}
    with pytest.raises(UnsupportedHookParams) as caught:
        define('hook_name', **unsupported_params)
    assert all(param_name in str(caught.value) for param_name in unsupported_params)

    hook = define('other_hook')
    with pytest.raises(UnsupportedHookParams) as caught:
        hook.configure(**unsupported_params)
    assert all(param_name in str(caught.value) for param_name in unsupported_params)


@pytest.mark.parametrize('stringify', [str, repr])
def test_hook_str_repr(stringify):
    assert stringify(Hook(get_global_group(), "some_name", arg_names=("a", "b"))) == \
        "<Hook some_name(a, b)>"


@pytest.fixture(name='doc_string')
def doc_string_fixture():
    return 'Some hook doc'
