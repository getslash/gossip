import logbook

import gossip


def test_deprecated_hook():
    with logbook.TestHandler(force_heavy_init=True) as h:

        hook = gossip.define('hook', deprecated=True)
        assert h.records == []

        @hook.register
        def handler():
            pass

        [r] = h.records

        assert r.filename == __file__
