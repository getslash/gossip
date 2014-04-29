import capnhook

def test_trigger_no_hook_registered():
    result = capnhook.trigger("unregistered")
    assert result is None
