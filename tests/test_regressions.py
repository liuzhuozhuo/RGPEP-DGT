"""Regression tests for the bugs listed in docs/assessment.md, mostly in the legacy engine."""
from math import comb, factorial

import numpy as np
import pytest

from src.core.pipeline import calculate_diagrams
from src.search.comparison import diagram_signature, group_diagrams
from src.transforms.concatenation import get_all_pairings, make_connection, matches_process
from src.transforms.simplify import simplify_diagram


@pytest.mark.parametrize("n_1, n_2", [(1, 1), (2, 3), (3, 3), (4, 2)])
def test_pairings_follow_wick_counting(n_1, n_2):
    # Contracting k of n_1 annihilation with k of n_2 creation operators can be done in C(n_1,k) C(n_2,k) k! ways
    expected = sum(comb(n_1, k) * comb(n_2, k) * factorial(k) for k in range(1, min(n_1, n_2) + 1))
    assert len(get_all_pairings(n_1, n_2)) == expected


def test_simplify_point_that_is_right_end_of_two_lines():
    # Point 4 is the right end of lines 1 and 3, so it has to be removed and those lines joined into 1-3.
    # Before the fix the case was not recognised because the line index was checked instead of the line end.
    points = np.array([[0, 1], [0, 3], [1, 1], [2, 2], [2, 3]])
    connections = np.array([[[1, 4], [2, 5], [3, 4]]])
    new_points, new_connections = simplify_diagram(points, connections)
    assert len(new_points) == 4
    assert sorted(map(tuple, np.sort(new_connections[0], axis=1))) == [(1, 3), (2, 4)]


def test_make_connection_mixes_any_number_of_types():
    # Diagram 1 has one incoming line of each of 3 types and diagram 2 one outgoing line of each type,
    # so there are 2^3 - 1 ways to connect them, one for each non-empty set of types
    points1 = np.array([[0, 2], [1, 2], [2, 1], [2, 2], [2, 3]])
    connections1 = np.array([[[1, 2], [2, 3]], [[2, 4], [0, 0]], [[2, 5], [0, 0]]])
    points2 = np.array([[0, 1], [0, 2], [0, 3], [1, 2], [2, 2]])
    connections2 = np.array([[[1, 4], [4, 5]], [[2, 4], [0, 0]], [[3, 4], [0, 0]]])
    _, connections = make_connection(points1, connections1, points2, connections2)

    def connected_types(connection):
        # A line between a point of diagram 1 (1..5) and a point of diagram 2 (6..10)
        return frozenset(t for t in range(3) for a, b in connection[t] if 0 < a <= 5 < b)

    found = [connected_types(c) for c in connections]
    assert len(found) == 7
    assert set(found) == {frozenset(s) for s in [{0}, {1}, {2}, {0, 1}, {0, 2}, {1, 2}, {0, 1, 2}]}


def test_matches_process_checks_every_type():
    # One incoming gluon and one outgoing quark (types 0 and 2), nothing else
    connections = np.array([[[1, 2], [0, 0]], [[0, 0], [0, 0]], [[2, 3], [0, 0]], [[0, 0], [0, 0]]])
    assert not matches_process(connections, [[1, 0, 0, 0], [0, 0, 1, 0]])
    # Lines: 1 -> 2 is a gluon whose left end 1 is outgoing; 2 -> 3 is a quark whose right end 3 is incoming
    assert matches_process(connections, [[0, 0, 1, 0], [1, 0, 0, 0]])
    # Types that are not listed count as 0 particles
    assert matches_process(connections, [[0, 0, 1], [1]])


@pytest.mark.parametrize("engine", ["new", "legacy"])
def test_complete_mode_only_returns_the_process(engine):
    for points, connections in zip(*calculate_diagrams("qcd", [0, 0, 1, 0], [0, 0, 1, 0], 2, engine=engine)[:2]):
        assert matches_process(connections, [[0, 0, 1, 0], [0, 0, 1, 0]])


def test_signature_does_not_depend_on_numbering_or_y():
    points = np.array([[0, 1], [0, 3], [1, 2], [2, 1], [2, 3]])
    connections = np.array([[[1, 3], [2, 3], [3, 4], [3, 5]]])
    # Swap the labels of points 4 and 5 and of 1 and 2, and move the vertex up
    relabel = {1: 2, 2: 1, 3: 3, 4: 5, 5: 4}
    new_points = np.array([points[relabel[v] - 1] for v in range(1, 6)]) + np.array([0, 7])
    new_connections = np.vectorize(lambda v: relabel.get(v, 0))(connections)
    assert diagram_signature(points, connections) == diagram_signature(new_points, new_connections)


def test_signature_distinguishes_vertex_order():
    # Same lines, but the vertex with the two outgoing lines comes first in one diagram and last in the other
    points = np.array([[0, 1], [0, 3], [1, 2], [2, 2], [3, 1], [3, 3]])
    connections = np.array([[[1, 3], [2, 3], [3, 4], [4, 5], [4, 6]]])
    swapped = np.array([[0, 1], [0, 3], [2, 2], [1, 2], [3, 1], [3, 3]])
    assert diagram_signature(points, connections) != diagram_signature(swapped, connections)


def test_group_diagrams_merges_relabelled_copies():
    points = np.array([[[0, 1], [0, 3], [1, 2], [2, 1], [2, 3]]] * 2)
    connections = np.array([[[[1, 3], [2, 3], [3, 4], [3, 5]]], [[[2, 3], [1, 3], [3, 5], [3, 4]]]])
    _, _, grouped_count = group_diagrams(points, connections, np.array([[1], [2]]))
    assert list(grouped_count) == [3]


@pytest.mark.parametrize("engine", ["new", "legacy"])
def test_first_order(engine):
    # Only a+a+a+a has 1 incoming and 3 outgoing particles. The legacy engine returns every first-order term.
    points, connections, count, _ = calculate_diagrams("phi4", 1, 3, 1, engine=engine)
    assert len(points) == (1 if engine == "new" else 3)


def test_framework_gluon_self_energy_has_gluon_and_quark_loop():
    # (a+aa)(a+a+a) and (a+db)(b+d+a). Both products have the same points and only differ in the type of particle
    # of the lines, so they were merged before. The quark loop also needs two types of particles to be connected
    # at the same time, which the in/out bookkeeping did not allow.
    points, paths, _, _ = calculate_diagrams("qcd", [1, 0, 0, 0], [1, 0, 0, 0], 2, mode="framework", engine="legacy")
    assert len(points) == 2
    assert np.array_equal(points[0], points[1])
    assert not np.array_equal(paths[0], paths[1])


def test_framework_respects_gluon_number_parity():
    # Every first-order QCD term has an odd number of gluon lines and a contraction removes 2,
    # so at third order there must be an odd number of external gluons
    points, _, _, _ = calculate_diagrams("qcd", [0, 0, 1, 0], [0, 0, 1, 0], 3, mode="framework", engine="legacy")
    assert len(points) == 0
