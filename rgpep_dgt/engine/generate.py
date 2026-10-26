"""
Generation of the diagrams of a given order and process, following the rules in docs/literature.md:

1. Every ordered product of initial terms whose orders add up to the order is considered once.
2. An incoming leg (annihilation operator) of a factor can only be contracted with an outgoing leg (creation
   operator) of the same type of particle in a factor further to the right.
3. A contraction pattern is kept if the factors can be split recursively into two contiguous groups with at least
   one contraction between the groups at every split (Glazek, Acta Phys. Pol. B 43, 1843 (2012), Eqs. (18), (24)).

Contractions are enumerated as numbers of lines between pairs of vertices instead of pairs of labelled legs. The
number of labelled contractions (Wick terms) that give the same lines is computed with a formula, see wick_count.
Products of terms are independent of each other, so they can be split among several processes (workers).
"""
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache
from math import factorial, prod


@dataclass(slots=True)
class Diagram:
    """
    n_vertices: number of vertices, numbered by their position in the product
    lines: sorted tuple of (type, vertex a, vertex b, number of lines) with a <= b, including internal lines of terms
    external: sorted tuple of (vertex, type, "out" or "in", number of lines)
    counterterms: sorted tuple of the vertices that are counterterms
    count: number of Wick contractions that give the diagram, summed over all products of terms
    weight: count with every product multiplied by the weights of its terms (e.g. 1/(k! l!) in phi^4). For a
        diagram whose external lines of each type and direction all attach to one vertex, weight * prod(n!) over
        those groups of n external lines is the usual 1/S, with S the symmetry factor.
    products: term sequence (tuple of term indices) -> count from that product, sorted by sequence
    n_factors, factor_pairs: number of terms in the product and (left, right) factors of every contraction
    """
    n_vertices: int
    lines: tuple
    external: tuple
    counterterms: tuple = ()
    count: int = 0
    weight: Fraction = Fraction(0)
    products: dict = field(default_factory=dict)
    n_factors: int = 0
    factor_pairs: frozenset = frozenset()

    @property
    def key(self):
        return self.n_vertices, self.lines, self.external, self.counterterms

    @property
    def bracketings(self):
        """Ways of building the product from products of two factors, as nested tuples of factor positions."""
        return bracketings(self.n_factors, self.factor_pairs)


def term_sequences(theory, order):
    """Every ordered sequence of term indices whose orders add up to order."""
    if order == 0:
        yield ()
        return
    for i, term in enumerate(theory.terms):
        if term.order <= order:
            for rest in term_sequences(theory, order - term.order):
                yield (i,) + rest


def feasible(terms, n_in, n_out, n_types):
    """Quick checks that a product of terms can give the process at all."""
    for t in range(n_types):
        total_in = sum(term.n_in(t) for term in terms)
        total_out = sum(term.n_out(t) for term in terms)
        # Every contraction removes one incoming and one outgoing line of the same type
        if total_in - n_in[t] != total_out - n_out[t] or total_in < n_in[t]:
            return False
        # Nothing can be contracted with the outgoing lines of the first factor or the incoming lines of the last one
        if terms[0].n_out(t) > n_out[t] or terms[-1].n_in(t) > n_in[t]:
            return False
    return True


@lru_cache(maxsize=None)
def has_bracketing(n_factors, factor_pairs):
    """True if bracketings(n_factors, factor_pairs) is not empty, without listing them."""
    # valid[lo][hi]: the factors lo..hi-1 can be bracketed. Filled from short to long groups.
    valid = [[False] * (n_factors + 1) for _ in range(n_factors + 1)]
    for lo in range(n_factors):
        valid[lo][lo + 1] = True
    for length in range(2, n_factors + 1):
        for lo in range(n_factors - length + 1):
            hi = lo + length
            valid[lo][hi] = any(valid[lo][m] and valid[m][hi] and any(lo <= i < m <= j < hi for i, j in factor_pairs)
                                for m in range(lo + 1, hi))
    return valid[0][n_factors]


@lru_cache(maxsize=4096)
def bracketings(n_factors, factor_pairs):
    """
    Every way of splitting the factors 0..n_factors-1 recursively into two contiguous groups with at least one
    contraction between the groups at every split. factor_pairs are the (left, right) factors of the contractions.
    """
    @lru_cache(maxsize=None)
    def trees(lo, hi):
        if hi - lo == 1:
            return (lo,)
        result = []
        for m in range(lo + 1, hi):
            if any(lo <= i < m <= j < hi for i, j in factor_pairs):
                result += [(left, right) for left in trees(lo, m) for right in trees(m, hi)]
        return tuple(result)

    return trees(0, n_factors)


def wick_count(out_legs, in_legs, contracted, external_out, external_in):
    """
    Number of labelled contractions that give the same numbers of lines between vertices.

    For every vertex and type, the incoming legs can be split among their destinations in in!/(prod m! e!) ways,
    and the same for the outgoing legs. The m chosen legs on both ends of the lines between two vertices can then
    be paired in m! ways. Together: prod in! prod out! / (prod m! prod e_in! prod e_out!).
    """
    numerator = prod(factorial(n) for legs in (out_legs, in_legs) for vertex in legs for n in vertex)
    denominator = prod(factorial(m) for m in contracted.values())
    denominator *= prod(factorial(n) for legs in (external_out, external_in) for vertex in legs for n in vertex)
    return numerator // denominator


def enumerate_contractions(terms, n_in, n_out, n_types, visit):
    """
    Call visit(contracted, external_out, external_in, factor_of) for every allowed way of contracting a product of
    terms that gives the process. contracted maps (type, vertex a, vertex b) to the number of lines from a to b.
    The arguments are only valid during the call (they are modified afterwards).

    The incoming legs are distributed vertex by vertex, from left to right. Outgoing legs of a factor can only be
    contracted with incoming legs of earlier factors, so once the first incoming leg of a factor is reached, the
    free outgoing legs of that factor and the earlier ones are final ("locked"). Branches are cut as soon as the
    locked legs, or the free legs that the remaining incoming legs cannot absorb, exceed the process.

    Plain recursion with a callback is used instead of generators: passing every result up a chain of nested
    generators costs as much as the enumeration itself.
    """
    factor_of, out_legs, in_legs = [], [], []
    for f, term in enumerate(terms):
        for out, inc in term.legs:
            factor_of.append(f)
            out_legs.append(list(out))
            in_legs.append(list(inc))
    n_vertices = len(factor_of)
    n_factors = len(terms)
    types = range(n_types)
    n_out = list(n_out)
    n_in = list(n_in)

    slots = [(u, t) for u in range(n_vertices) for t in types if in_legs[u][t] > 0]
    n_slots = len(slots)
    # Incoming legs of each type in the slots s, s+1, ...
    remaining_in = [[sum(in_legs[u][t] for u, t2 in slots[s:] if t2 == t) for t in types] for s in range(n_slots + 1)]
    # Vertices whose outgoing legs become final when slot s is reached (all the remaining ones at the end)
    slot_factors = [factor_of[u] for u, _ in slots] + [n_factors - 1]
    lock_at = [[v for v in range(n_vertices) if (slot_factors[s-1] if s else -1) < factor_of[v] <= slot_factors[s]]
               for s in range(n_slots + 1)]
    targets_of = [[v for v in range(n_vertices) if factor_of[v] > factor_of[u] and out_legs[v][t] > 0]
                  for u, t in slots]

    free_out = [list(out) for out in out_legs]
    free_total = [sum(out[t] for out in out_legs) for t in types]
    locked = [0] * n_types
    external_in = [[0] * n_types for _ in range(n_vertices)]
    external_in_total = [0] * n_types
    contracted = {}

    def possible(s):
        remaining = remaining_in[s]
        for t in types:
            if locked[t] > n_out[t]:
                return False
            # At most this many more lines of type t can still be contracted
            absorbable = min(remaining[t], free_total[t] - locked[t])
            if free_total[t] - absorbable > n_out[t] or external_in_total[t] + remaining[t] - absorbable > n_in[t]:
                return False
        return True

    def distribute(s, k, u, t, targets, left):
        # Send `left` incoming legs of type t of vertex u to the vertices targets[k:], or leave them external
        if k == len(targets):
            if external_in_total[t] + left <= n_in[t]:
                external_in[u][t] = left
                external_in_total[t] += left
                fill(s + 1)
                external_in_total[t] -= left
                external_in[u][t] = 0
            return
        v = targets[k]
        free = free_out[v]
        for m in range(min(left, free[t]), 0, -1):
            free[t] -= m
            free_total[t] -= m
            contracted[(t, u, v)] = m
            distribute(s, k + 1, u, t, targets, left - m)
            del contracted[(t, u, v)]
            free_total[t] += m
            free[t] += m
        distribute(s, k + 1, u, t, targets, left)

    def fill(s):
        newly_locked = lock_at[s]
        for v in newly_locked:
            for t in types:
                locked[t] += free_out[v][t]
        if possible(s):
            if s == n_slots:
                if free_total == n_out and external_in_total == n_in:
                    visit(contracted, free_out, external_in, factor_of)
            else:
                u, t = slots[s]
                distribute(s, 0, u, t, targets_of[s], in_legs[u][t])
        for v in newly_locked:
            for t in types:
                locked[t] -= free_out[v][t]

    fill(0)


def contractions(terms, n_in, n_out, n_types):
    """
    List of (contracted, external_out, external_in, factor_of) for every allowed way of contracting a product of
    terms, see enumerate_contractions. Unlike there, the values are copies and stay valid.
    """
    found = []
    enumerate_contractions(terms, n_in, n_out, n_types, lambda c, o, i, f: found.append(
        (dict(c), [list(x) for x in o], [list(x) for x in i], list(f))))
    return found


FACTORIAL = [factorial(n) for n in range(64)]


def _generate_products(theory, sequences, n_in, n_out):
    """
    Diagrams of the given products of terms, as a dict key -> [count, products, n_factors, factor_pairs]. The weight
    is computed at the end from the counts of the products (exact fractions are too slow to add up for every
    contraction).
    """
    n_types = theory.n_types
    found = {}
    # Many diagrams share the same lines and external lines; storing one copy of each tuple saves most of the memory
    shared = {}
    for sequence in sequences:
        terms = [theory.terms[i] for i in sequence]
        if not feasible(terms, n_in, n_out, n_types):
            continue

        # Vertices of the product and the internal lines of the terms, with vertices numbered in the product
        offsets = [sum(term.n_vertices for term in terms[:f]) for f in range(len(terms))]
        n_vertices = offsets[-1] + terms[-1].n_vertices
        # Internal lines of the terms never join the same vertices as a contraction (those join different terms)
        internal = [(t, a, b, m) for (t, a, b), m in
                    Counter((t, a + offsets[f], b + offsets[f]) for f, term in enumerate(terms) for t, a, b in term.lines).items()]
        multiplicity = prod(term.count for term in terms)
        counterterms = tuple(offsets[f] + k for f, term in enumerate(terms) if term.counterterm
                             for k in range(term.n_vertices))
        # The numerator of wick_count only depends on the product of terms
        numerator = prod(FACTORIAL[n] for term in terms for out, inc in term.legs for n in out + inc)

        def visit(contracted, external_out, external_in, factor_of):
            factor_pairs = frozenset((factor_of[u], factor_of[v]) for _, u, v in contracted)
            if not has_bracketing(len(terms), factor_pairs):
                return
            denominator = prod(FACTORIAL[m] for m in contracted.values())
            external = []
            for v in range(n_vertices):
                for t in range(n_types):
                    # Sorted as (vertex, type, "in" before "out")
                    if external_in[v][t]:
                        e = (v, t, "in", external_in[v][t])
                        external.append(shared.setdefault(e, e))
                        denominator *= FACTORIAL[external_in[v][t]]
                    if external_out[v][t]:
                        e = (v, t, "out", external_out[v][t])
                        external.append(shared.setdefault(e, e))
                        denominator *= FACTORIAL[external_out[v][t]]
            count = multiplicity * (numerator // denominator)

            lines = tuple(sorted(internal + [shared.setdefault(line, line) for line in
                                             ((t, a, b, m) for (t, a, b), m in contracted.items())]))
            external = tuple(external)
            key = (n_vertices, shared.setdefault(lines, lines), shared.setdefault(external, external), counterterms)
            entry = found.get(key)
            if entry is None:
                entry = found[key] = [0, {}, len(terms), factor_pairs]
            entry[0] += count
            entry[1][sequence] = entry[1].get(sequence, 0) + count

        enumerate_contractions(terms, n_in, n_out, n_types, visit)
    return found


def _merge(results):
    merged = {}
    for found in results:
        for key, (count, products, n_factors, factor_pairs) in found.items():
            entry = merged.get(key)
            if entry is None:
                merged[key] = [count, dict(products), n_factors, factor_pairs]
            else:
                entry[0] += count
                for sequence, c in products.items():
                    entry[1][sequence] = entry[1].get(sequence, 0) + c
    return merged


def generate_diagrams(theory, order, n_in, n_out, workers=1, cache=False):
    """
    All diagrams of a given order for the process with n_in incoming and n_out outgoing particles of each type.

    Args:
        theory (Theory): the theory, see rgpep_dgt/engine/theory.py
        order (int): order in the coupling constant
        n_in, n_out (list or int): number of incoming/outgoing particles of each type (an int means the first type)
        workers (int or None): number of processes to use, None for one per CPU. Worth it only for large orders.
        cache (bool or str): keep the result on disk and reuse it, see rgpep_dgt/engine/cache.py. A string is the
            directory to use.
    Returns:
        list of Diagram, sorted by their key
    """
    n_types = theory.n_types
    pad = lambda n: ([n] if isinstance(n, int) else list(n)) + [0] * (n_types - (1 if isinstance(n, int) else len(n)))
    n_in, n_out = pad(n_in), pad(n_out)

    if cache:
        from rgpep_dgt.engine.cache import cached
        return cached(theory, order, n_in, n_out, workers, None if cache is True else cache)

    sequences = [sequence for sequence in term_sequences(theory, order)
                 if feasible([theory.terms[i] for i in sequence], n_in, n_out, n_types)]
    workers = os.cpu_count() if workers is None else workers
    if workers > 1 and len(sequences) > 1:
        # One task per product, the ones with most legs (usually the longest) first so they do not finish last
        size = lambda sequence: sum(theory.terms[i].n_in(t) for i in sequence for t in range(n_types))
        sequences.sort(key=size, reverse=True)
        with ProcessPoolExecutor(max_workers=min(workers, len(sequences))) as pool:
            results = list(pool.map(_generate_products, [theory] * len(sequences), [[s] for s in sequences],
                                    [n_in] * len(sequences), [n_out] * len(sequences)))
        found = _merge(results)
    else:
        found = _generate_products(theory, sequences, n_in, n_out)

    term_weights = {}

    def product_weight(sequence):
        if sequence not in term_weights:
            term_weights[sequence] = prod((theory.terms[i].weight for i in sequence), start=Fraction(1))
        return term_weights[sequence]

    diagrams = []
    for key in sorted(found):
        count, products, n_factors, factor_pairs = found[key]
        if len(products) == 1:
            (sequence, c), = products.items()
            w = product_weight(sequence)
            weight = Fraction(c * w.numerator, w.denominator)
        else:
            weight = sum((product_weight(sequence) * c for sequence, c in products.items()), start=Fraction(0))
        diagrams.append(Diagram(*key, count=count, weight=weight, products=dict(sorted(products.items())),
                                n_factors=n_factors, factor_pairs=factor_pairs))
    return diagrams


def term_products(theory, order, n_in, n_out, workers=1, cache=False):
    """Products of terms that contribute to the process, with their total count (the old "framework" mode)."""
    products = Counter()
    for diagram in generate_diagrams(theory, order, n_in, n_out, workers=workers, cache=cache):
        products.update(diagram.products)
    return dict(sorted(products.items()))
