"""Parallel generation, disk cache and pruning give the same diagrams as the plain computation."""
import pytest

from rgpep_dgt import calculate_diagrams, generate_diagrams, get_theory
from rgpep_dgt.engine.generate import contractions
from rgpep_dgt.engine.theory import Term


def as_dict(diagrams):
    return {d.key: (d.count, d.weight, d.products, d.n_factors, d.factor_pairs) for d in diagrams}


@pytest.mark.parametrize("name, order, n_in, n_out", [
    ("phi4", 5, 2, 2), ("qcd", 3, [0, 0, 1, 0], [1, 0, 1, 0]), ("qcd_gluons", 4, [1, 0], [1, 0])])
def test_parallel_gives_the_same_diagrams(name, order, n_in, n_out):
    theory = get_theory(name)
    serial = generate_diagrams(theory, order, n_in, n_out)
    parallel = generate_diagrams(theory, order, n_in, n_out, workers=4)
    assert [d.key for d in serial] == [d.key for d in parallel]
    assert as_dict(serial) == as_dict(parallel)


def test_cache_returns_the_same_diagrams_and_is_reused(tmp_path):
    theory = get_theory("phi4")
    first = generate_diagrams(theory, 4, 2, 2, cache=str(tmp_path))
    files = list(tmp_path.glob("*.pkl"))
    assert len(files) == 1
    second = generate_diagrams(theory, 4, 2, 2, cache=str(tmp_path))
    assert as_dict(first) == as_dict(second) == as_dict(generate_diagrams(theory, 4, 2, 2))
    assert list(tmp_path.glob("*.pkl")) == files  # read, not written again


def test_cache_depends_on_theory_and_process(tmp_path):
    theory = get_theory("phi4")
    generate_diagrams(theory, 3, 2, 2, cache=str(tmp_path))
    generate_diagrams(theory, 3, 1, 3, cache=str(tmp_path))
    generate_diagrams(get_theory("phi4", True, 3), 3, 2, 2, cache=str(tmp_path))
    assert len(list(tmp_path.glob("*.pkl"))) == 3


def test_broken_cache_file_is_recomputed(tmp_path):
    theory = get_theory("phi4")
    generate_diagrams(theory, 3, 1, 1, cache=str(tmp_path))
    (path,) = tmp_path.glob("*.pkl")
    path.write_bytes(b"not a pickle")
    assert as_dict(generate_diagrams(theory, 3, 1, 1, cache=str(tmp_path))) == \
        as_dict(generate_diagrams(theory, 3, 1, 1))


def test_calculate_diagrams_passes_workers_and_cache(tmp_path):
    plain = calculate_diagrams("phi4", 2, 2, 4)
    other = calculate_diagrams("phi4", 2, 2, 4, workers=2, cache=str(tmp_path))
    assert (plain[2] == other[2]).all()
    assert as_dict(plain[3]) == as_dict(other[3])


def test_pruning_does_not_lose_contractions():
    # A product where many branches are cut: (a+a+a+a)(a+aaa) in phi^4. For 3 -> 3 there is only one way to
    # contract (one line), which the pruning must keep, and for 1 -> 1 none.
    a3, b3 = Term(1, (((3,), (1,)),)), Term(1, (((1,), (3,)),))
    assert len(contractions([a3, b3], [3], [3], 1)) == 1
    assert contractions([a3, b3], [1], [1], 1) == []
    assert len(contractions([b3, a3], [1], [1], 1)) == 1  # (a+aaa)(a+a+a+a): all three lines
