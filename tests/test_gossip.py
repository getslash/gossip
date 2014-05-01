import gossip

def test_register_trigger(hook_name, handler):
    gossip.register(func=handler, hook_name=hook_name)
    gossip.trigger(hook_name)
    assert handler.num_called == 1
