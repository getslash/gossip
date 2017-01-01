import gossip

import pytest


def test_non_strict_hook_doesnt_validate(request):
    hook = gossip.define('somegroup.somehook', arg_names={'x': None, 'y': int})
    request.addfinalizer(hook.undefine)

    hook.trigger(kwargs={})

def test_strict_hook_without_argument_defs_doesnt_validate(request):
    group = gossip.get_or_create_group('somegroup')
    group.set_strict()
    request.addfinalizer(group.undefine)
    hook = gossip.define('somegroup.somehook')
    request.addfinalizer(hook.undefine)

    hook.trigger(kwargs={'bla': 2, 'some': 'string', 'and_an': object()})



@pytest.mark.parametrize('kwargs', [
    {},
    {'x': 1},
    {'x': 1, 'y': 2},
])
def test_strict_hook_validate_arg_names(validating_hook, kwargs):
    with pytest.raises(TypeError) as excinfo:
        validating_hook.trigger(kwargs=kwargs)

    excinfo.match('Missing argument .*')


@pytest.mark.parametrize('kwargs', [
    {'x': 1, 'y': 'str', 'z': 's'},
    {'x': 1, 'y': 'str', 'z': 's'},
    {'x': 1, 'y': 2, 'z': 3},
    {'x': 1, 'y': 's', 'z': 2.0},
])
def test_strict_hook_validate_arg_types(validating_hook, kwargs):
    with pytest.raises(TypeError) as excinfo:
        validating_hook.trigger(kwargs=kwargs)

    excinfo.match('Incorrect type')


@pytest.mark.parametrize('kwargs', [
    {'x': 1, 'y': 2, 'z': 's'},
    {'x': 1, 'y': 3, 'z': 3.0},
    {'x': object(), 'y': 2, 'z': 3.2},
])
def test_strict_hook_correct_arg_names_and_types(validating_hook, kwargs):
    validating_hook.trigger(kwargs=kwargs)



@pytest.fixture
def validating_hook(request):

    group = gossip.get_or_create_group('some_strict_group')
    group.set_strict()
    request.addfinalizer(group.undefine)

    hook = gossip.define('some_strict_group.some_hook', arg_names={'x': None, 'y': int, 'z': (str, float)})
    request.addfinalizer(hook.undefine)
    return hook
