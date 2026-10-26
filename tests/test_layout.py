"""Placement of the points of diagrams for drawing."""
from itertools import combinations

import pytest

from rgpep_dgt import generate_diagrams, get_theory
from rgpep_dgt.engine.arrays import diagram_to_arrays
from rgpep_dgt.engine.layout import X_ASPECT, _cross, _distance


def drawn_segments(diagram, n_types):
    points, connections = diagram_to_arrays(diagram, n_types)
    visual = [(X_ASPECT * x, y) for x, y in points]
    segments = {tuple(sorted((int(a) - 1, int(b) - 1))) for t in range(n_types) for a, b in connections[t] if a != b}
    return points, visual, sorted(segments)


CLEAN_CASES = [
    ("qcd_gluons", True, 3, [1, 0], [2, 0]),   # Gomez-Rocha and Glazek, Fig. 7
    ("phi4", False, 2, 2, 2),
    ("phi4", False, 3, 1, 1),
    ("qcd", False, 2, [0, 0, 1, 1], [0, 0, 1, 1]),
    ("qcd", False, 3, [0, 0, 1, 0], [1, 0, 1, 0]),
]


@pytest.mark.parametrize("name, counterterms, order, n_in, n_out", CLEAN_CASES)
def test_no_crossing_lines_and_no_point_on_another_line(name, counterterms, order, n_in, n_out):
    theory = get_theory(name, counterterms, order if counterterms else None)
    for diagram in generate_diagrams(theory, order, n_in, n_out):
        _, visual, segments = drawn_segments(diagram, theory.n_types)
        for (a, b), (c, d) in combinations(segments, 2):
            if len({a, b, c, d}) == 4:
                assert not _cross(visual[a], visual[b], visual[c], visual[d]), diagram.key
        for a, b in segments:
            for p in range(len(visual)):
                if p not in (a, b):
                    assert _distance(visual[p], visual[a], visual[b]) > 0.3, diagram.key


def test_x_positions_follow_the_product_and_external_points_are_on_the_sides():
    theory = get_theory("qcd")
    for diagram in generate_diagrams(theory, 3, [0, 0, 1, 0], [1, 0, 1, 0]):
        points, _, _ = drawn_segments(diagram, theory.n_types)
        n = diagram.n_vertices
        assert [x for x, _ in points[:n]] == list(range(1, n + 1))
        assert all(x in (0, n + 1) for x, _ in points[n:])
        assert min(y for _, y in points) == 1


def test_external_points_on_one_side_do_not_overlap():
    theory = get_theory("phi4")
    for diagram in generate_diagrams(theory, 3, 2, 2):
        points, _, _ = drawn_segments(diagram, theory.n_types)
        n = diagram.n_vertices
        for side in (0, n + 1):
            heights = sorted(y for x, y in points[n:] if x == side)
            assert all(b - a >= 1 for a, b in zip(heights, heights[1:]))


def test_layout_is_deterministic():
    theory = get_theory("qcd_gluons", True, 3)
    first = [diagram_to_arrays(d, 2)[0].tolist() for d in generate_diagrams(theory, 3, [1, 0], [2, 0])]
    second = [diagram_to_arrays(d, 2)[0].tolist() for d in generate_diagrams(theory, 3, [1, 0], [2, 0])]
    assert first == second
