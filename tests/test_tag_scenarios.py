from munch import Munch
from .utils import UnitestSteps, _noop

import pytest
import gossip
from gossip.exceptions import UndefinedHook, UnsupportedHookTags


steps = UnitestSteps()

@steps.add
def _make_group_strict(ctx):
    raises_context = _noop()
    if ctx.registered_hook:
        if not ctx.defined_hook:
            raises_context = pytest.raises(UndefinedHook)
        elif not ctx.is_tags_valid_for_strict_group:
            raises_context = pytest.raises(UnsupportedHookTags)
    with raises_context:
        gossip.get_or_create_group("group").set_strict()
    ctx.made_strict = True

@steps.add
def _make_define_hook(ctx):
    gossip.define("group.defined_hook", tags=ctx.defined_tags)
    ctx.defined_hook = True

@steps.add
def _make_register_hook(ctx):
    raises_context = _noop()
    if ctx.made_strict:
        if not ctx.defined_hook:
            raises_context = pytest.raises(UndefinedHook)
        elif not ctx.is_tags_valid_for_strict_group:
            raises_context = pytest.raises(UnsupportedHookTags)

    with raises_context:
        @gossip.register("group.defined_hook", tags=ctx.registeration_tags)
        def handler():  # pylint: disable=unused-variable
            pass
    ctx.registered_hook = True

def _clean_workspace():
    gossip.registry.hooks = {}
    gossip.registry.groups = {None: gossip.registry.groups[None]}

@pytest.mark.parametrize("tags_info", [
    (None, None, True),
    (None, ("fake_tag",), False),
    (None, ("fake_tag", "fake_tag2"), False),
    (tuple(), None, True),
    (tuple(), ("fake_tag",), False),
    (tuple(), ("fake_tag", "fake_tag2"), False),
    (("some_tag",), None, True),
    (("some_tag",), tuple(), True),
    (("some_tag",), ("some_tag",), True),
    (("some_tag",), ("fake_tag",), False),
    (("some_tag",), ("some_tag", "fake_tag"), False),
    (("some_tag",), ("fake_tag", "fake_tag2"), False),
    (("some_tag", "other_tag"), None, True),
    (("some_tag", "other_tag"), tuple(), True),
    (("some_tag", "other_tag"), ("some_tag",), True),
    (("some_tag", "other_tag"), ("fake_tag",), False),
    (("some_tag", "other_tag"), ("some_tag", "fake_tag"), False),
    (("some_tag", "other_tag"), ("some_tag", "other_tag"), True),
    (("some_tag", "other_tag"), ("fake_tag", "fake_tag2"), False),
    ])
@steps.get_all_permutations
def test_tags(tags_info, steps):
    defined_tags, registered_tags, valid_strict_tags = tags_info
    ctx = Munch(
        made_strict=False,
        defined_hook=False,
        registered_hook=False,
        defined_tags=defined_tags,
        registeration_tags=registered_tags,
        is_tags_valid_for_strict_group=valid_strict_tags,
        )
    _clean_workspace()
    for step_func in steps:
        step_func(ctx)

def test_single_set_tags_per_hook():
    some_hook = gossip.define('group.some_hook')
    other_hook = gossip.define('group.other_hook', tags=("other_tag",))
    some_hook.set_tags(('some_tag',))

    with pytest.raises(AssertionError):
        some_hook.set_tags(('some_other_tag',))

    with pytest.raises(AssertionError):
        other_hook.set_tags(('some_other_tag',))

def test_trigger_hook_with_unsupported_tags():
    gossip.define('group.some_hook', tags=("some_tag",))
    gossip.trigger('group.some_hook', tags=("fake_tag",))
    gossip.get_or_create_group('group').set_strict()
    with pytest.raises(UnsupportedHookTags):
        gossip.trigger_with_tags('group.some_hook', tags=("fake_tag",))


@pytest.mark.parametrize("hook_name", ["main_group1.some_hook", "main_group2.sub_group.other_hook"])
def test_set_strict_with_subgroups_and_tags(hook_name):
    def handler():
        pass

    main_group_name = hook_name.partition(".")[0]
    gossip.register(handler, hook_name)

    with pytest.raises(UndefinedHook):
        gossip.get_or_create_group(main_group_name).set_strict()
    hook = gossip.define(hook_name, tags=("some_tag", "other_tag"))

    illegal_tags_hook = gossip.define(".".join([hook.group.full_name, "hook_with_illegal_tags"]))
    gossip.register(handler, illegal_tags_hook.full_name, tags=("fake_tag"))
    with pytest.raises(UnsupportedHookTags):
        gossip.get_or_create_group(main_group_name).set_strict()
    illegal_tags_hook.unregister_all()

    gossip.get_or_create_group(main_group_name).set_strict()
    with pytest.raises(UnsupportedHookTags):
        @gossip.register(hook_name, tags=("fake_tag",))
        def handler2():  # pylint: disable=unused-variable
            pass
    with pytest.raises(UnsupportedHookTags):
        gossip.trigger_with_tags(hook_name, tags=("fake_tag",))
    gossip.trigger_with_tags(hook_name, tags=("some_tag", "other_tag"))
