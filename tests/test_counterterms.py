"""Counterterms and weights (symmetry factors) of the new engine."""
from fractions import Fraction

import numpy as np
import pytest

from rgpep_dgt import calculate_diagrams, generate_diagrams, get_theory
from rgpep_dgt.engine.arrays import diagram_to_arrays, key_from_arrays


def counterterm_names(name, max_order):
    return sorted((t.order, t.name) for t in get_theory(name, True, max_order).terms if t.counterterm)


def test_gluon_counterterms_follow_gomez_rocha_glazek():
    # Gomez-Rocha and Glazek, PRD 92, 065005 (2015): gluon mass counterterm at second order and three-gluon vertex
    # counterterm at third order, nothing else up to third order
    assert counterterm_names("qcd_gluons", 3) == [(2, "CT2_mass_gluon"), (3, "CT3_H1_1"), (3, "CT3_H1_2")]


def test_qcd_has_mass_counterterms_for_every_particle_and_vertex_counterterms():
    names = counterterm_names("qcd", 3)
    assert [n for o, n in names if o == 2] == ["CT2_mass_antiquark", "CT2_mass_gluon", "CT2_mass_quark"]
    assert len([n for o, n in names if o == 3]) == 8  # one per first-order term


def test_phi4_coupling_counterterm_already_at_second_order():
    # The one-loop correction to the four-point vertex is of order lambda^2 in phi^4
    assert (2, "CT2_H1_1") in counterterm_names("phi4", 2)


def test_three_gluon_vertex_third_order_with_counterterms_has_all_ten_diagrams():
    # Fig. 7 of Gomez-Rocha and Glazek: the 7 diagrams without counterterms, plus (f) and (i) mass counterterms on
    # the outgoing and incoming legs, and (j) the vertex counterterm
    diagrams = generate_diagrams(get_theory("qcd_gluons", True, 3), 3, [1, 0], [2, 0])
    assert len(diagrams) == 10
    with_counterterm = [d for d in diagrams if d.counterterms]
    assert len(with_counterterm) == 3
    vertex = [d for d in with_counterterm if d.n_vertices == 1]
    assert len(vertex) == 1 and vertex[0].count == 1                                    # (j)
    mass = {d.counterterms: d.count for d in with_counterterm if d.n_vertices == 2}
    # Mass counterterm first: on one of the two outgoing gluons (2 ways). Second: on the incoming gluon.
    assert mass == {(0,): 2, (1,): 1}


def test_counterterms_appear_with_the_loops_they_cancel():
    gluon = calculate_diagrams("qcd_gluons", [1, 0], [1, 0], 2, counterterms=True)[2]
    assert sorted(gluon) == [1, 2]       # mass counterterm and gluon loop
    phi4 = calculate_diagrams("phi4", 2, 2, 2, counterterms=True)[2]
    assert sorted(phi4) == [1, 2, 18]    # coupling counterterm and the two loops


def test_no_counterterm_without_a_correction():
    # Three gluons at second order: no diagram, so no counterterm either
    assert generate_diagrams(get_theory("qcd_gluons", True, 3), 2, [1, 0], [2, 0]) == []


def test_counterterm_vertices_are_marked_in_the_arrays():
    for diagram in generate_diagrams(get_theory("qcd_gluons", True, 3), 3, [1, 0], [2, 0]):
        points, connections = diagram_to_arrays(diagram, 2)
        markers = [v for a, b in connections[0] if a == b != 0 for v in [a]]
        assert len(markers) == len(diagram.counterterms)
        assert key_from_arrays(points, connections) == diagram.key


# Weights: with the normalisation 1/(k! l!) of phi^4/4!, weight times the factorials of the external lines is the
# symmetry factor 1/S of the corresponding Feynman diagram (Peskin & Schroeder, Sec. 4.4)

def find(diagrams, lines, external):
    matches = [d for d in diagrams if d.lines == lines and d.external == external]
    assert len(matches) == 1
    return matches[0]


def test_sunset_symmetry_factor():
    # Three lines between the two vertices: S = 3!
    (sunset,) = generate_diagrams(get_theory("phi4"), 2, 1, 1)
    assert sunset.weight == Fraction(1, 6)


def test_bubble_symmetry_factor():
    # Two lines between the vertices, both incoming particles on one vertex and both outgoing on the other: S = 2
    bubble = find(generate_diagrams(get_theory("phi4"), 2, 2, 2), ((0, 0, 1, 2),),
                  ((0, 0, "out", 2), (1, 0, "in", 2)))
    assert bubble.weight * 2 * 2 == Fraction(1, 2)


def test_chain_of_two_bubbles_symmetry_factor():
    # S = 2 * 2
    chain = find(generate_diagrams(get_theory("phi4"), 3, 2, 2), ((0, 0, 1, 2), (0, 1, 2, 2)),
                 ((0, 0, "out", 2), (2, 0, "in", 2)))
    assert chain.weight * 2 * 2 == Fraction(1, 4)


def test_weights_are_counts_when_terms_have_no_normalisation():
    for diagram in generate_diagrams(get_theory("qcd"), 2, [1, 0, 0, 0], [1, 0, 0, 0]):
        assert diagram.weight == diagram.count
