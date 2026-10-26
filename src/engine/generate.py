"""
Generation of the diagrams of a given order and process, following the rules in docs/literature.md:

1. Every ordered product of initial terms whose orders add up to the order is considered once.
2. An incoming leg (annihilation operator) of a factor can only be contracted with an outgoing leg (creation
   operator) of the same type of particle in a factor further to the right.
3. A contraction pattern is kept if the factors can be split recursively into two contiguous groups with at least
   one contraction between the groups at every split (Glazek, Acta Phys. Pol. B 43, 1843 (2012), Eqs. (18), (24)).

Contractions are enumerated as numbers of lines between pairs of vertices instead of pairs of labelled legs. The
number of labelled contractions (Wick terms) that give the same lines is computed with a formula, see wick_count.
"""
from collections import Counter
from dataclasses import dataclass, field
from functools import cached_property, lru_cache
from math import factorial, prod


@dataclass
class Diagram:
    """
    n_vertices: number of vertices, numbered by their position in the product
    lines: sorted tuple of (type, vertex a, vertex b, number of lines) with a <= b, including internal lines of terms
    external: sorted tuple of (vertex, type, "out" or "in", number of lines)
    count: number of Wick contractions that give the diagram, summed over all products of terms
    products: term sequence (tuple of term indices) -> count from that product
    n_factors, factor_pairs: number of terms in the product and (left, right) factors of every contraction
    """
    n_vertices: int
    lines: tuple
    external: tuple
    count: int = 0
    products: Counter = field(default_factory=Counter)
    n_factors: int = 0
    factor_pairs: frozenset = frozenset()

    @property
    def key(self):
        return self.n_vertices, self.lines, self.external

    @cached_property
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
    @lru_cache(maxsize=None)
    def valid(lo, hi):
        if hi - lo == 1:
            return True
        return any(valid(lo, m) and valid(m, hi) and any(lo <= i < m <= j < hi for i, j in factor_pairs)
                   for m in range(lo + 1, hi))

    return valid(0, n_factors)


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


def contractions(terms, n_in, n_out, n_types):
    """
    Yield (contracted, external_out, external_in, factor_of) for every allowed way of contracting a product of terms
    that gives the process. contracted maps (type, vertex a, vertex b) to the number of lines from a to b.
    """
    factor_of, out_legs, in_legs = [], [], []
    for f, term in enumerate(terms):
        for out, inc in term.legs:
            factor_of.append(f)
            out_legs.append(list(out))
            in_legs.append(list(inc))
    n_vertices = len(factor_of)

    free_out = [list(out) for out in out_legs]  # outgoing legs not contracted yet
    external_in = [[0] * n_types for _ in range(n_vertices)]
    external_in_total = [0] * n_types
    contracted = Counter()
    slots = [(u, t) for u in range(n_vertices) for t in range(n_types) if in_legs[u][t] > 0]
    # The outgoing legs of a factor can only be contracted with incoming legs of earlier factors. So when the first
    # slot of a factor is reached, the outgoing legs of that factor and the ones before it are final.
    first_slot_of_factor = [s == 0 or factor_of[slots[s-1][0]] != factor_of[u] for s, (u, _) in enumerate(slots)]
    vertices_up_to = [[v for v in range(n_vertices) if factor_of[v] <= f] for f in range(len(terms))]

    def outgoing_ok(last_factor):
        return all(sum(free_out[v][t] for v in vertices_up_to[last_factor]) <= n_out[t] for t in range(n_types))

    def distribute(k, u, t, targets, left):
        # Send `left` incoming legs of type t of vertex u to the vertices targets[k:], or leave them external
        if k == len(targets):
            if external_in_total[t] + left <= n_in[t]:
                external_in[u][t] = left
                external_in_total[t] += left
                yield from fill(slots_index[(u, t)] + 1)
                external_in_total[t] -= left
                external_in[u][t] = 0
            return
        v = targets[k]
        for m in range(min(left, free_out[v][t]), -1, -1):
            if m:
                free_out[v][t] -= m
                contracted[(t, u, v)] += m
            yield from distribute(k + 1, u, t, targets, left - m)
            if m:
                free_out[v][t] += m
                contracted[(t, u, v)] -= m
                if contracted[(t, u, v)] == 0:
                    del contracted[(t, u, v)]

    def fill(s):
        if s == len(slots):
            if all(sum(free_out[v][t] for v in range(n_vertices)) == n_out[t] and external_in_total[t] == n_in[t]
                   for t in range(n_types)):
                yield dict(contracted), [list(o) for o in free_out], [list(i) for i in external_in], factor_of
            return
        u, t = slots[s]
        if first_slot_of_factor[s] and not outgoing_ok(factor_of[u]):
            return
        targets = [v for v in range(n_vertices) if factor_of[v] > factor_of[u] and free_out[v][t] > 0]
        yield from distribute(0, u, t, targets, in_legs[u][t])

    slots_index = {slot: s for s, slot in enumerate(slots)}
    yield from fill(0)


def generate_diagrams(theory, order, n_in, n_out):
    """
    All diagrams of a given order for the process with n_in incoming and n_out outgoing particles of each type.

    Args:
        theory (Theory): the theory, see src/engine/theory.py
        order (int): order in the coupling constant
        n_in, n_out (list or int): number of incoming/outgoing particles of each type (an int means the first type)
    Returns:
        list of Diagram, sorted by their key
    """
    n_types = theory.n_types
    pad = lambda n: ([n] if isinstance(n, int) else list(n)) + [0] * (n_types - (1 if isinstance(n, int) else len(n)))
    n_in, n_out = pad(n_in), pad(n_out)

    diagrams = {}
    for sequence in term_sequences(theory, order):
        terms = [theory.terms[i] for i in sequence]
        if not feasible(terms, n_in, n_out, n_types):
            continue

        # Vertices of the product and the internal lines of the terms, with vertices numbered in the product
        offsets = [sum(term.n_vertices for term in terms[:f]) for f in range(len(terms))]
        out_legs = [list(out) for term in terms for out, _ in term.legs]
        in_legs = [list(inc) for term in terms for _, inc in term.legs]
        internal = Counter((t, a + offsets[f], b + offsets[f]) for f, term in enumerate(terms) for t, a, b in term.lines)
        multiplicity = prod(term.count for term in terms)

        for contracted, external_out, external_in, factor_of in contractions(terms, n_in, n_out, n_types):
            factor_pairs = frozenset((factor_of[u], factor_of[v]) for _, u, v in contracted)
            if not has_bracketing(len(terms), factor_pairs):
                continue
            count = multiplicity * wick_count(out_legs, in_legs, contracted, external_out, external_in)

            lines = internal + Counter(contracted)
            external = [(v, t, "out", external_out[v][t]) for v in range(len(out_legs)) for t in range(n_types)
                        if external_out[v][t]]
            external += [(v, t, "in", external_in[v][t]) for v in range(len(in_legs)) for t in range(n_types)
                         if external_in[v][t]]
            diagram = Diagram(n_vertices=len(out_legs), lines=tuple(sorted((t, a, b, m) for (t, a, b), m in lines.items())),
                              external=tuple(sorted(external)), n_factors=len(terms), factor_pairs=factor_pairs)
            diagram = diagrams.setdefault(diagram.key, diagram)
            diagram.count += count
            diagram.products[sequence] += count

    return [diagrams[key] for key in sorted(diagrams)]


def term_products(theory, order, n_in, n_out):
    """Products of terms that contribute to the process, with their total count (the old "framework" mode)."""
    products = Counter()
    for diagram in generate_diagrams(theory, order, n_in, n_out):
        products.update(diagram.products)
    return dict(sorted(products.items()))
