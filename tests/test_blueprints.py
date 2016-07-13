import gossip
from gossip import Blueprint
from gossip.exceptions import UndefinedHook

import pytest


def test_multiple_functions_same_hook(blueprint, checkpoint):  # pylint: disable=unused-argument

    called = set()

    @blueprint.register('a')
    def handler1():  # pylint: disable=unused-variable
        called.add(1)

    @blueprint.register('a')
    def handler2():  # pylint: disable=unused-variable
        called.add(2)

    blueprint.install()
    gossip.trigger('a')
    assert called == set([1, 2])


def test_blueprint(blueprint, checkpoint):

    @blueprint.register('a.b')
    def handler():  # pylint: disable=unused-variable
        checkpoint()

    gossip.trigger('a.b')

    assert not checkpoint.called

    blueprint.install()

    gossip.trigger('a.b')
    assert checkpoint.called


def test_uninstall(blueprint, checkpoint):

    blueprint.register('a')(checkpoint)
    blueprint.install()
    gossip.trigger('a')
    assert checkpoint.called
    checkpoint.reset()
    blueprint.uninstall()
    gossip.trigger('a')
    assert not checkpoint.called


def test_exception_on_register(blueprint):

    gossip.get_or_create_group('group').set_strict()

    @blueprint.register('group.a')
    def func():  # pylint: disable=unused-variable
        pass

    @blueprint.register('x')
    def func():  # pylint: disable=function-redefined
        pass

    with pytest.raises(UndefinedHook):
        blueprint.install()

    assert len(gossip.get_all_registrations()) == 0


def test_blueprint_register_prefix(blueprint, checkpoint):

    @gossip.register('a')
    def handler():  # pylint: disable=unused-variable
        pass

    @blueprint.register('a')
    def handler():  # pylint: disable=function-redefined
        checkpoint()

    assert len(gossip.get_all_registrations()) == 1

    blueprint.install(group='group')

    gossip.trigger('a')
    assert not checkpoint.called

    gossip.trigger('group.a')

    assert checkpoint.called



@pytest.fixture
def blueprint():
    return Blueprint()
