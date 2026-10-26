"""Tests of the new engine in src/engine."""
from collections import Counter
from itertools import product
from math import factorial

import numpy as np
import pytest

from src.core.pipeline import calculate_diagrams
from src.engine.arrays import diagram_to_arrays, key_from_arrays
from src.engine.generate import bracketings, generate_diagrams, term_products, wick_count
from src.engine.theory import get_theory


def test_phi4_terms_read_from_canonical_diagrams():
    # a+a+aa, a+a+a+a and a+aaa, as (outgoing, incoming) lines of the field phi
    legs = sorted((term.legs[0][0][0], term.legs[0][1][0]) for term in get_theory("phi4").terms)
    assert legs == [(1, 3), (2, 2), (3, 1)]


def test_instantaneous_terms_have_two_vertices_and_an_internal_line():
    for term in get_theory("qcd_gluons").terms:
        if term.order == 2:
            assert term.n_vertices == 2
            assert term.lines == ((1, 0, 1),)  # type 1 is the instantaneous line


def test_wick_count_matches_labelled_enumeration():
    # Vertex 0 has 3 incoming legs, vertex 1 has 3 outgoing legs. Send 2 lines from 0 to 1 and count the labelled
    # pairings by brute force: choose 2 of 3 incoming legs, 2 of 3 outgoing legs and pair them.
    labelled = sum(1 for ins in product(range(3), repeat=2) for outs in product(range(3), repeat=2)
                   if len(set(ins)) == 2 and len(set(outs)) == 2) // 2
    count = wick_count(out_legs=[[0], [3]], in_legs=[[3], [0]], contracted={(0, 0, 1): 2},
                       external_out=[[0], [1]], external_in=[[1], [0]])
    assert count == labelled == 3 * 3 * factorial(2)


@pytest.mark.parametrize("pairs, expected", [
    ({(0, 1), (1, 2)}, {((0, 1), 2), (0, (1, 2))}),  # both bracketings work
    ({(0, 1), (0, 2)}, {((0, 1), 2)}),               # factors 1 and 2 are not contracted with each other
    ({(0, 2), (1, 2)}, {(0, (1, 2))}),               # factors 0 and 1 are not contracted with each other
    ({(0, 2)}, set()),                               # factor 1 is not connected
])
def test_bracketings_of_three_factors(pairs, expected):
    assert set(bracketings(3, frozenset(pairs))) == expected


def test_connected_pattern_without_bracketing_is_excluded():
    # Contractions 0-2, 0-3 and 1-3 connect all four factors, but every split leaves a group that is not connected
    assert bracketings(4, frozenset({(0, 2), (0, 3), (1, 3)})) == ()


def test_diagram_arrays_round_trip():
    for diagram in generate_diagrams(get_theory("qcd"), 2, [0, 0, 1, 1], [0, 0, 1, 1]):
        points, connections = diagram_to_arrays(diagram, 4)
        assert key_from_arrays(points, connections) == diagram.key


QCD_CASES = [
    ("qcd_gluons", [1, 0], [1, 0]), ("qcd_gluons", [2, 0], [2, 0]), ("qcd_gluons", [1, 0], [3, 0]),
    ("qcd", [1, 0, 0, 0], [1, 0, 0, 0]), ("qcd", [0, 0, 1, 0], [0, 0, 1, 0]), ("qcd", [0, 0, 1, 1], [0, 0, 1, 1]),
]


def legacy_diagrams(theory, n_in, n_out, order):
    points, connections, count, _ = calculate_diagrams(theory, n_in, n_out, order, engine="legacy")
    diagrams = Counter()
    for p, c, k in zip(points, connections, np.ravel(count)):
        diagrams[key_from_arrays(p, c)] += int(k)
    return diagrams


@pytest.mark.parametrize("theory, n_in, n_out", QCD_CASES)
def test_same_as_legacy_at_second_order(theory, n_in, n_out):
    # The legacy engine is correct at second order (see docs/roadmap.md, step 1)
    new = {d.key: d.count for d in generate_diagrams(get_theory(theory), 2, n_in, n_out)}
    assert new == dict(legacy_diagrams(theory, n_in, n_out, 2))


@pytest.mark.parametrize("theory, n_in, n_out", [("qcd_gluons", [1, 0], [2, 0]), ("qcd", [0, 0, 1, 0], [1, 0, 1, 0])])
def test_same_diagrams_as_legacy_at_third_order(theory, n_in, n_out):
    # Same diagrams, but the legacy engine counts some contractions more than once
    new = {d.key: d.count for d in generate_diagrams(get_theory(theory), 3, n_in, n_out)}
    old = legacy_diagrams(theory, n_in, n_out, 3)
    assert set(new) == set(old)
    assert all(new[key] <= old[key] for key in new)
    assert any(new[key] < old[key] for key in new)


def test_framework_gluon_self_energy():
    # Gluon loop (a+aa)(a+a+a), 2 ways, and quark loop (a+db)(b+d+a), 1 way
    theory = get_theory("qcd")
    products = {tuple(theory.terms[i].name for i in sequence): count
                for sequence, count in term_products(theory, 2, [1, 0, 0, 0], [1, 0, 0, 0]).items()}
    assert products == {("H1_2", "H1_1"): 2, ("H1_8", "H1_7"): 1}


def test_framework_includes_instantaneous_terms():
    # Unlike the legacy framework mode, products with second-order (instantaneous) terms are included
    theory = get_theory("qcd_gluons")
    orders = {tuple(theory.terms[i].order for i in sequence) for sequence in term_products(theory, 3, [1, 0], [2, 0])}
    assert orders == {(1, 1, 1), (1, 2), (2, 1)}


def test_every_count_is_a_sum_over_its_products():
    for diagram in generate_diagrams(get_theory("qcd"), 3, [0, 0, 1, 0], [1, 0, 1, 0]):
        assert diagram.count == sum(diagram.products.values()) > 0
        assert diagram.bracketings
