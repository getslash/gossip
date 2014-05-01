import gossip

def test_register_trigger(registered_hook):
    assert registered_hook.works()

def test_unregister(registered_hook):
    assert registered_hook.works()
    registered_hook.func.gossip.unregister()
    assert not registered_hook.works()

def test_unregister_all(registered_hooks):
    assert all(r.works() for r in registered_hooks)
    gossip.unregister_all()
    assert all(not r.works() for r in registered_hooks)

def test_unregister_all_specific(registered_hooks):
    gossip.unregister_all(registered_hooks[0].name)
    assert not registered_hooks[0].works()
    assert all(r.works for r in registered_hooks[1:])
