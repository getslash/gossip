import pytest
import itertools
from contextlib import contextmanager


@contextmanager
def _noop():
    yield

class UnitestSteps(object):
    def __init__(self, param_name=None):
        self._steps = []
        self._got_permutations = False
        self._param_name = param_name or "steps"

    def add(self, func):
        assert not self._got_permutations, "Cannot add step after got permutations"
        self._steps.append(func)

    def get_all_permutations(self, func):
        self._got_permutations = True
        return pytest.mark.parametrize(self._param_name, itertools.permutations(self._steps))(func)
