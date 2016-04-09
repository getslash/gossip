import gossip


def test_normal_hooks_can_reenter(counter):
    counter.set(5)

    @gossip.register('reentrant_hook')
    def handler(): # pylint: disable=unused-variable
        counter.sub(1)
        if counter:
            gossip.trigger('reentrant_hook')

    gossip.trigger('reentrant_hook')
    assert counter == 0


def test_non_reentrant_hooks(counter):
    hook_name = 'nonreentrant_hook'


    @gossip.register(hook_name, reentrant=False)
    def handler(): # pylint: disable=unused-variable
        counter.add(1)
        gossip.trigger(hook_name)

    gossip.trigger(hook_name)
    assert counter == 1
