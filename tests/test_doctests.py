from __future__ import print_function
import os
import doctest

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

@pytest.mark.parametrize("path", [
    os.path.join(path, filename)
    for path, _, filenames in os.walk(os.path.join(PROJECT_ROOT, 'doc'))
    for filename in filenames
    if filename.endswith((".rst", ".md"))])
def test_doctests(path):
    assert os.path.exists(path)
    result = doctest.testfile(path, module_relative=False)
    assert result.failed == 0
