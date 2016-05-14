#pylint: disable=unused-variable
import gossip
import pytest


@pytest.mark.parametrize('should_raise', [True, False])
def test_toggle_hooks(should_raise):

    events = []

    toggle = gossip.Toggle()
    assert toggle.is_off()

    @gossip.register('start')
    def malicious():
        events.append('malicious')
        if should_raise:
            raise CustomException()

    @gossip.register('start', toggles_on=toggle)
    def start():
        events.append('start')

    @gossip.register('end', toggles_off=toggle)
    def end():
        events.append('end')

    if should_raise:
        with pytest.raises(CustomException):
            gossip.trigger('start')
    else:
        gossip.trigger('start')

    assert toggle.is_on() == (not should_raise)

    gossip.trigger('end')

    assert toggle.is_off()

    assert len(events) == len(set(events))
    if should_raise:
        assert 'start' not in events
        assert 'end' not in events
    else:
        assert events.index('malicious') < events.index('start')
        assert 'end' in events


class CustomException(Exception):
    pass
