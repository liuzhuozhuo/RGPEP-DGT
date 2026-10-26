"""
Independent brute-force reference for the RGPEP operator structures of a theory with one type of particle.

It does not use any code from src/, so it can be used to check the diagram generation. The rules come from
Glazek, Acta Phys. Pol. B 43, 1843 (2012), arXiv:1204.4760 (see docs/literature.md):

1. The term of order n is a sum over ordered products of n first-order terms, each ordered product appearing
   once (Eqs. (B.6)-(B.11)).
2. In a product, an annihilation operator of a factor can only be contracted with a creation operator of a factor
   further to the right (normal-ordered terms, Wick's theorem).
3. The products come from Eq. (24), G'_n = sum_k A G_k G_{n-k}, where every product of two operators keeps only
   the terms with at least one contraction between them (text below Eq. (18)). A contraction pattern is therefore
   kept if the factors can be split recursively into two contiguous groups with at least one contraction between
   the two groups at every split.

A vertex is described by (number of outgoing lines, number of incoming lines), i.e. (creation, annihilation)
operators. The count of a diagram is the number of different contractions (Wick terms) that give it.
"""
from collections import Counter
from functools import lru_cache
from itertools import product


def _contraction_sets(vertices):
    """Yield every set of contractions as a tuple of (left factor, in leg, right factor, out leg)."""
    n = len(vertices)
    in_legs = [(i, leg) for i in range(n) for leg in range(vertices[i][1])]
    used_out = set()
    chosen = []

    def assign(k):
        if k == len(in_legs):
            yield tuple(chosen)
            return
        i, leg = in_legs[k]
        # The in leg stays external
        yield from assign(k + 1)
        # Or it is contracted with a free out leg of a factor further to the right
        for j in range(i + 1, n):
            for out_leg in range(vertices[j][0]):
                if (j, out_leg) not in used_out:
                    used_out.add((j, out_leg))
                    chosen.append((i, leg, j, out_leg))
                    yield from assign(k + 1)
                    chosen.pop()
                    used_out.discard((j, out_leg))

    yield from assign(0)


def _is_rgpep_term(n, pairs):
    """True if the factors 0..n-1 can be split recursively with at least one contraction across every split."""
    pairs = frozenset(pairs)

    @lru_cache(maxsize=None)
    def valid(lo, hi):
        if hi - lo == 1:
            return True
        return any(valid(lo, m) and valid(m, hi) and any(lo <= i < m <= j < hi for i, j in pairs)
                   for m in range(lo + 1, hi))

    return valid(0, n)


def rgpep_diagrams(vertex_types, order, n_in, n_out):
    """
    Counts of the diagrams of a given order and process.

    Args:
        vertex_types (list): (out, in) lines of every first-order term of the theory
        order (int): order in the coupling constant
        n_in, n_out (int): number of incoming and outgoing particles
    Returns:
        Counter mapping a diagram signature to the number of contractions that give it. The signature is
        (lines between factors, external lines of each factor), with factors labelled by their position.
    """
    diagrams = Counter()
    for vertices in product(vertex_types, repeat=order):
        for contractions in _contraction_sets(vertices):
            pairs = [(i, j) for i, _, j, _ in contractions]
            if not _is_rgpep_term(order, pairs):
                continue
            used_in = Counter(i for i, _, _, _ in contractions)
            used_out = Counter(j for _, _, j, _ in contractions)
            external = tuple((vertices[v][0] - used_out[v], vertices[v][1] - used_in[v]) for v in range(order))
            if sum(e[1] for e in external) != n_in or sum(e[0] for e in external) != n_out:
                continue
            diagrams[(tuple(sorted(Counter(pairs).items())), external)] += 1
    return diagrams


# Front-form phi^4: a+a+aa, a+a+a+a and a+aaa. Terms with only creation or only annihilation operators vanish
# because p+ > 0 for every particle.
PHI4_VERTICES = [(2, 2), (3, 1), (1, 3)]
