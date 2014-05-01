import gossip

def test_trigger_no_hook_registered():
    result = gossip.trigger("unregistered")
    assert result is None
