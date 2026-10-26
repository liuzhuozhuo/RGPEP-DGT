"""calculate_diagrams and the array format helpers."""
import numpy as np

from rgpep_dgt.core.array_format import matches_process
from rgpep_dgt.core.pipeline import calculate_diagrams


def test_matches_process_checks_every_type():
    # One incoming gluon and one outgoing quark (types 0 and 2), nothing else
    connections = np.array([[[1, 2], [0, 0]], [[0, 0], [0, 0]], [[2, 3], [0, 0]], [[0, 0], [0, 0]]])
    assert not matches_process(connections, [[1, 0, 0, 0], [0, 0, 1, 0]])
    # Lines: 1 -> 2 is a gluon whose left end 1 is outgoing; 2 -> 3 is a quark whose right end 3 is incoming
    assert matches_process(connections, [[0, 0, 1, 0], [1, 0, 0, 0]])
    # Types that are not listed count as 0 particles
    assert matches_process(connections, [[0, 0, 1], [1]])


def test_complete_mode_only_returns_the_process():
    for points, connections in zip(*calculate_diagrams("qcd", [0, 0, 1, 0], [0, 0, 1, 0], 2)[:2]):
        assert matches_process(connections, [[0, 0, 1, 0], [0, 0, 1, 0]])


def test_first_order():
    # Only a+a+a+a has 1 incoming and 3 outgoing particles
    points, connections, count, _ = calculate_diagrams("phi4", 1, 3, 1)
    assert len(points) == 1 and list(count) == [1]


def test_framework_mode_returns_products():
    points, paths, _, products = calculate_diagrams("qcd", [1, 0, 0, 0], [1, 0, 0, 0], 2, mode="framework")
    assert len(points) == len(paths) == len(products) == 2
