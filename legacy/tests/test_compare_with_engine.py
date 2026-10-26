"""Comparison of the legacy engine with rgpep_dgt.engine."""
from collections import Counter

import numpy as np
import pytest

from legacy.pipeline import calculate_diagrams
from rgpep_dgt.engine.arrays import key_from_arrays
from rgpep_dgt.engine.generate import generate_diagrams
from rgpep_dgt.engine.theory import get_theory


QCD_CASES = [
    ("qcd_gluons", [1, 0], [1, 0]), ("qcd_gluons", [2, 0], [2, 0]), ("qcd_gluons", [1, 0], [3, 0]),
    ("qcd", [1, 0, 0, 0], [1, 0, 0, 0]), ("qcd", [0, 0, 1, 0], [0, 0, 1, 0]), ("qcd", [0, 0, 1, 1], [0, 0, 1, 1]),
]


def legacy_diagrams(theory, n_in, n_out, order):
    points, connections, count, _ = calculate_diagrams(theory, n_in, n_out, order)
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
