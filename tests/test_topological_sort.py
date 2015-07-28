import pytest
from gossip.exceptions import CannotResolveDependencies
from gossip.utils import _topological_sort


def test_topological_sort(indices, graph, expected):
    sorted = _topological_sort(indices, set(graph))
    assert len(sorted) == len(indices)
    assert set(sorted) == set(indices)
    assert sorted == expected


def test_cycles():
    with pytest.raises(CannotResolveDependencies):
        _topological_sort([0, 1, 2, 3], set([(0, 1), (1, 2), (2, 0)]))


@pytest.fixture(params=[
    (set([(0, 1), (1, 2)]), [0, 1, 2, 3, 4]),
    (set([(4, 0), (2, 4), (3, 2)]), [1, 3, 2, 4, 0]),
    (set([(4, 0), (2, 4), (3, 1), (3, 2)]), [3, 2, 4, 0, 1]),
    ])
def graph_expected(request):
    return request.param

@pytest.fixture
def graph(graph_expected):
    return graph_expected[0]

@pytest.fixture
def expected(graph_expected):
    return graph_expected[1]


@pytest.fixture
def indices():
    return list(range(5))
