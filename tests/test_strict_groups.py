from munch import Munch

import gossip
from gossip.exceptions import UndefinedHook
from .utils import TestSteps, _noop
import pytest


def test_undefined_hooks_have_no_side_effects():
    assert gossip.get_all_registrations() == []
    gossip.get_or_create_group('group').set_strict()

    for retry in range(5):
        with pytest.raises(UndefinedHook):
            @gossip.register('group.hook')
            def handler():
                pass
    assert gossip.get_all_registrations() == []


steps = TestSteps()

@steps.add
def _make_group_strict(ctx):
    if ctx.registered_undefined_hook or (ctx.registered_defined_hook and not ctx.defined_hook):
        raises_context = pytest.raises(UndefinedHook)
    else:
        raises_context = _noop()

    with raises_context:
        gossip.get_or_create_group("group").set_strict()
        ctx.made_strict = True

@steps.add
def _register_undefined_hook(ctx):
    if ctx.made_strict:
        raises_context = pytest.raises(UndefinedHook)
    else:
        raises_context = _noop()
    with raises_context:
        @gossip.register('group.undefined_hook')
        def handler():
            pass
    ctx.registered_undefined_hook = True

@steps.add
def _register_defined_hook(ctx):
    if ctx.made_strict and not ctx.defined_hook:
        raises_context = pytest.raises(UndefinedHook)
    else:
        raises_context = _noop()
    with raises_context:
        @gossip.register('group.defined_hook')
        def handler():
            pass
    ctx.registered_defined_hook = True

@steps.add
def _define_hook(ctx):
    gossip.define("group.defined_hook")
    ctx.defined_hook = True


@steps.get_all_permutations
def test_strict_groups(steps):
    ctx = Munch(
        made_strict=False,
        defined_hook=False,
        registered_undefined_hook=False,
        registered_defined_hook=False,
    )
    for step_func in steps:
        step_func(ctx)

def test_make_group_not_strict():
    group = gossip.get_or_create_group('group')
    subgroup = gossip.get_or_create_group('group.sub')
    assert not group.is_strict()
    assert not subgroup.is_strict()

    group.set_strict()
    assert group.is_strict()
    assert subgroup.is_strict()

    group.set_strict(False)
    assert not group.is_strict()
    assert not subgroup.is_strict()
