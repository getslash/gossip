import hooky

def test_trigger_no_hook_registered():
    result = hooky.trigger("unregistered")
    assert result is None
