import itertools

from .exceptions import CannotResolveDependencies
from .helpers import DONT_CARE, FIRST, LAST

def topological_sort_registrations(registrations, unconstrained_priority=DONT_CARE):
    graph = _build_dependency_graph(registrations, unconstrained_priority=unconstrained_priority)
    returned_indices = _topological_sort(range(len(registrations)), graph)
    assert len(returned_indices) == len(registrations)
    return [registrations[idx] for idx in returned_indices]


def _topological_sort(indices, graph):
    independent = sorted(set(indices) - set(m for n, m in graph), reverse=True)
    returned = []
    while independent:
        n = independent.pop()
        returned.append(n)
        for m in indices:
            edge = (n, m)
            if m == n:
                assert edge not in graph
                continue
            if edge in graph:
                graph.remove(edge)
                # check if m is now independent
                for edge in graph:
                    if edge[1] == m:
                        # not indepdendent
                        break
                else:
                    # no other incoming edges to m
                    independent.append(m)
    if graph:
        raise CannotResolveDependencies('Cyclic dependency detected')
    return returned


def _build_dependency_graph(registrations, unconstrained_priority):
    providers_by_name = {}
    for index, registration in enumerate(registrations):
        for name in registration.provides:
            providers = providers_by_name.get(name)
            if providers is None:
                providers = providers_by_name[name] = []
            providers.append(index)

    graph = set()
    for needer_index, registration in enumerate(registrations):
        for need in registration.needs:
            for provider_index in providers_by_name.get(need, []):
                graph.add((provider_index, needer_index))


    if unconstrained_priority != DONT_CARE:
        caring_indices = set([idx for idx, r in enumerate(registrations) if r.needs or r.provides])
        non_caring_indices = set(range(len(registrations))) - caring_indices
        for caring_index, uncaring_index in itertools.product(caring_indices, non_caring_indices):
            if unconstrained_priority == FIRST:
                pair = (uncaring_index, caring_index)
            else:
                pair = (caring_index, uncaring_index)
            graph.add(pair)


    return graph
