"""
Checks of the generated diagrams against results that follow from the literature, see docs/literature.md.

The counts are the number of Wick contractions of an ordered product of Hamiltonian terms that give a diagram.
Second-order values are derived by hand in docs/literature.md. Higher orders are compared with the independent
brute-force enumeration in tests/wick_reference.py.
"""
from collections import Counter

import numpy as np
import pytest

from src.core.pipeline import calculate_diagrams
from src.transforms.concatenation import in_out_connections
from wick_reference import PHI4_VERTICES, rgpep_diagrams


ENGINES = ["new", "legacy"]


def counts(theory, in_particles, out_particles, order, engine):
    points, connections, count, _ = calculate_diagrams(theory, in_particles, out_particles, order, engine=engine)
    return sorted(int(c) for c in np.ravel(count))


def reference_signature(points, connections):
    """
    Signature of a phi^4 diagram from src/ in the format of wick_reference: lines between vertices labelled by
    their position in the product, and (outgoing, incoming) external lines of each vertex.
    """
    lines = [(int(a), int(b)) for a, b in connections[0] if a != 0 or b != 0]
    in_out = in_out_connections(np.array([lines]))
    incoming = set(np.trim_zeros(in_out[0, 0]).tolist())
    outgoing = set(np.trim_zeros(in_out[0, 1]).tolist())
    internal = sorted({v for line in lines for v in line} - incoming - outgoing, key=lambda v: points[v-1, 0])
    position = {v: k for k, v in enumerate(internal)}

    between = Counter()
    external = [[0, 0] for _ in internal]
    for a, b in lines:
        if a in outgoing:
            external[position[b]][0] += 1
        elif b in incoming:
            external[position[a]][1] += 1
        else:
            between[tuple(sorted((position[a], position[b])))] += 1
    return tuple(sorted(between.items())), tuple(tuple(e) for e in external)


def code_diagrams(order, n_in, n_out, engine):
    points, connections, count, _ = calculate_diagrams("phi4", n_in, n_out, order, engine=engine)
    diagrams = Counter()
    for p, c, k in zip(points, connections, np.ravel(count)):
        diagrams[reference_signature(p, c)] += int(k)
    return diagrams


# Second order, derived by hand in docs/literature.md

@pytest.mark.parametrize("n_in, n_out, expected", [
    (1, 1, [6]),      # (a+aaa)(a+a+a+a), 3 contractions: 3!
    (2, 2, [2, 18]),  # (a+a+aa)(a+a+aa), 2 contractions: 2!; (a+aaa)(a+a+a+a), 2 contractions: 3*3*2!
    (1, 3, [6]),      # (a+a+aa)(a+a+a+a), 2 contractions: 3*2!
])
@pytest.mark.parametrize("engine", ENGINES)
def test_phi4_second_order(n_in, n_out, expected, engine):
    assert counts("phi4", n_in, n_out, 2, engine) == expected


@pytest.mark.parametrize("engine", ENGINES)
def test_gluon_self_energy_second_order(engine):
    # (a+aa)(a+a+a) with both gluons contracted: 2!
    assert counts("qcd_gluons", [1, 0], [1, 0], 2, engine) == [2]


@pytest.mark.parametrize("engine", ENGINES)
def test_gluon_2_to_2_second_order(engine):
    # (a+a+a)(a+aa): 1 contraction, 1 way. (a+aa)(a+a+a): 1 contraction, 2*2 ways. The other two are the
    # instantaneous terms of the canonical Hamiltonian as drawn in src/can_diagrams/qcd/gluons: 1 s-channel
    # diagram and 4 t-channel diagrams that only differ by the labels of the external gluons.
    assert counts("qcd_gluons", [2, 0], [2, 0], 2, engine) == [1, 1, 4, 4]


@pytest.mark.parametrize("engine", ENGINES)
def test_qcd_gluon_self_energy_second_order(engine):
    # Quark loop (a+db)(b+d+a): 1 way. Gluon loop (a+aa)(a+a+a): 2! ways.
    assert counts("qcd", [1, 0, 0, 0], [1, 0, 0, 0], 2, engine) == [1, 2]


@pytest.mark.parametrize("process", [([0, 0, 1, 0], [0, 0, 1, 0]), ([0, 0, 0, 1], [0, 0, 0, 1])])
@pytest.mark.parametrize("engine", ENGINES)
def test_qcd_quark_self_energy_second_order(process, engine):
    # (b+ab)(b+a+b) with the gluon and the quark contracted: 1 way, same for antiquarks
    assert counts("qcd", *process, 2, engine) == [1]


@pytest.mark.parametrize("engine", ENGINES)
def test_gluons_odd_order_cannot_give_four_gluons(engine):
    # Every term has an odd number of gluon lines at odd order (3 per H_A^3, 4 per instantaneous term),
    # and a contraction removes 2, so 2 -> 2 is impossible at third order.
    assert counts("qcd_gluons", [2, 0], [2, 0], 3, engine) == []


def describe(points, connections, type_names="gi"):
    """Lines between vertices (labelled by position in the product) and external lines of each vertex."""
    lines = [(t, int(a), int(b)) for t in range(len(connections)) for a, b in connections[t] if a != 0 or b != 0]
    in_out = in_out_connections(np.array(connections))
    incoming = set(np.trim_zeros(in_out[:, 0].ravel()).tolist())
    outgoing = set(np.trim_zeros(in_out[:, 1].ravel()).tolist())
    internal = sorted({v for _, a, b in lines for v in (a, b)} - incoming - outgoing, key=lambda v: points[v-1, 0])
    position = {v: k for k, v in enumerate(internal)}
    between, external = Counter(), Counter()
    for t, a, b in lines:
        if a in outgoing:
            external[(position[b], "out")] += 1
        elif b in incoming:
            external[(position[a], "in")] += 1
        else:
            between[(type_names[t],) + tuple(sorted((position[a], position[b])))] += 1
    return frozenset(between.items()), frozenset(external.items())


@pytest.mark.parametrize("engine", ENGINES)
def test_three_gluon_vertex_third_order_matches_gomez_rocha_glazek(engine):
    # Gomez-Rocha and Glazek, PRD 92, 065005 (2015), Fig. 7: contributions (a)-(j) to the third-order three-gluon
    # term a+ a+ a. (f), (i) and (j) are counterterms, which are not generated yet, the other 7 have to appear.
    # Quartic terms are drawn as two 3-gluon vertices joined by an instantaneous line i, as in that paper.
    g, i = "g", "i"
    out2_in = {((0, "out"), 1), ((1, "out"), 1), ((2, "in"), 1)}       # externals on three different vertices
    out_in_on_last = {((0, "out"), 1), ((2, "out"), 1), ((2, "in"), 1)}  # bubble on an outgoing leg
    outs_first = {((0, "out"), 2), ((2, "in"), 1)}                       # bubble on the incoming leg
    expected = {
        (frozenset({((g, 0, 1), 1), ((g, 0, 2), 1), ((g, 1, 2), 1)}), frozenset(out2_in)),         # (a)
        (frozenset({((i, 0, 1), 1), ((g, 0, 2), 1), ((g, 1, 2), 1)}), frozenset(out2_in)),         # (b)/(c)
        (frozenset({((g, 0, 1), 1), ((g, 0, 2), 1), ((i, 1, 2), 1)}), frozenset(out2_in)),         # (b)/(c)
        (frozenset({((g, 0, 1), 2), ((g, 1, 2), 1)}), frozenset(out_in_on_last)),                  # (d)/(g)
        (frozenset({((g, 0, 1), 1), ((g, 1, 2), 2)}), frozenset(outs_first)),                      # (d)/(g)
        (frozenset({((g, 0, 1), 2), ((i, 1, 2), 1)}), frozenset(out_in_on_last)),                  # (e)/(h)
        (frozenset({((i, 0, 1), 1), ((g, 1, 2), 2)}), frozenset(outs_first)),                      # (e)/(h)
    }
    points, connections, _, _ = calculate_diagrams("qcd_gluons", [1, 0], [2, 0], 3, engine=engine)
    assert {describe(p, c) for p, c in zip(points, connections)} == expected
    assert len(points) == 7


# Higher orders, compared with the brute-force reference

@pytest.mark.parametrize("engine", ENGINES)
@pytest.mark.parametrize("order, n_in, n_out", [(3, 1, 1), (3, 2, 2), (3, 1, 3), (4, 1, 1)])
def test_phi4_same_diagrams_as_reference(order, n_in, n_out, engine):
    assert set(code_diagrams(order, n_in, n_out, engine)) == set(rgpep_diagrams(PHI4_VERTICES, order, n_in, n_out))


LEGACY_OVERCOUNTS = pytest.mark.xfail(strict=True, reason=(
    "The legacy engine builds the same ordered product both as (H H) H and H (H H), so a contraction that both "
    "bracketings allow is counted more than once. Glazek's Eq. (31) has a single operator with summed coefficients."))


@pytest.mark.parametrize("engine", ["new", pytest.param("legacy", marks=LEGACY_OVERCOUNTS)])
@pytest.mark.parametrize("order, n_in, n_out", [(3, 1, 1), (3, 2, 2), (3, 1, 3), (4, 1, 1)])
def test_phi4_counts_match_reference(order, n_in, n_out, engine):
    assert code_diagrams(order, n_in, n_out, engine) == rgpep_diagrams(PHI4_VERTICES, order, n_in, n_out)


def test_reference_matches_hand_counts():
    # The reference must agree with the hand-derived values used above
    assert sorted(rgpep_diagrams(PHI4_VERTICES, 2, 1, 1).values()) == [6]
    assert sorted(rgpep_diagrams(PHI4_VERTICES, 2, 2, 2).values()) == [2, 18]
    assert sorted(rgpep_diagrams(PHI4_VERTICES, 2, 1, 3).values()) == [6]
    # (a+aaa)(a+a+aa)(a+a+a+a): 3*2 ways for the 2 lines to the middle, 3 for the line to the right, 2 for the rest
    assert sorted(rgpep_diagrams(PHI4_VERTICES, 3, 1, 1).values()) == [36]
