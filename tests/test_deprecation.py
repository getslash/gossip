from contextlib import contextmanager

import warnings
import gossip


def test_deprecated_hook():
    with python_warnings_recording() as recorded:

        hook = gossip.define('hook', deprecated=True)
        assert recorded == []  # pylint: disable=use-implicit-booleaness-not-comparison

        @hook.register
        def handler():  # pylint: disable=unused-variable
            pass

        [rec] = recorded  # pylint: disable=unbalanced-tuple-unpacking

        assert rec.filename == __file__


@contextmanager
def python_warnings_recording():
    warnings.simplefilter('always')
    with warnings.catch_warnings(record=True) as recorded:
        yield recorded
