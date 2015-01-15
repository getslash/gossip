import gossip
import pytest

_HOOK_NAME = 'some_group.some_hook'
_ACCEPTED_TAGS = ('tag1', 'tag2')
_INCOMPATIBLE_TAG_SETS = (
    ('tag11',),
    ('tag1', 'tag2', 'unknown'),
)


def test_trigger_hook(specify_tags):
    if specify_tags:
        gossip.trigger_with_tags(_HOOK_NAME, tags=_ACCEPTED_TAGS)
    else:
        gossip.trigger_with_tags(_HOOK_NAME, tags=())


@pytest.mark.parametrize('tags', _INCOMPATIBLE_TAG_SETS)
def test_trigger_with_bad_tags(tags, is_strict):
    if not is_strict:
        return
    with pytest.raises(gossip.exceptions.UnsupportedHookTags):
        gossip.trigger_with_tags(_HOOK_NAME, tags=tags)


@pytest.mark.parametrize('tags', _INCOMPATIBLE_TAG_SETS)
def test_register_with_bad_tags(tags, is_strict):
    if not is_strict:
        return

    def func():
        pass

    with pytest.raises(gossip.exceptions.UnsupportedHookTags):
        func = gossip.register(_HOOK_NAME, tags=tags)(func)

@pytest.fixture(params=[True, False])
def register_before_define(request):
    return request.param

@pytest.fixture(params=[True, False])
def create_group_before_define(request):
    return request.param

@pytest.fixture(params=[True, False, 'strict'])
def is_defined(request):
    return request.param

@pytest.fixture
def is_strict(is_defined):
    returned = not isinstance(is_defined, bool)
    assert not returned or is_defined == 'strict'
    return returned

@pytest.fixture(params=[True, False])
def specify_tags(request):
    return request.param


@pytest.fixture(autouse=True)
def setup_hook(is_defined, is_strict, specify_tags, register_before_define, create_group_before_define):
    # note: the combination of register before define *and* create strict group
    # before define is guaranteed to create an error
    if register_before_define:
        if not is_strict or not create_group_before_define:
            gossip.register(_HOOK_NAME)(lambda: None)

    if create_group_before_define:
        _get_or_create_group(is_strict)

    if is_defined:
        if specify_tags:
            gossip.define(_HOOK_NAME, tags=_ACCEPTED_TAGS)
        else:
            gossip.define(_HOOK_NAME)

    if not create_group_before_define:
        _get_or_create_group(is_strict)

def _get_or_create_group(is_strict):
    g = gossip.get_or_create_group(_HOOK_NAME.split('.')[0])
    if is_strict:
        g.set_strict()
