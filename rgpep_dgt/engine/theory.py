"""
Theories described as lists of initial Hamiltonian terms.

A term is a small diagram made of one or more vertices, ordered from left to right as in the product of operators.
Every vertex has external legs: outgoing legs (creation operators) and incoming legs (annihilation operators), counted
per type of particle. A term can also have internal lines between its own vertices, e.g. a quartic term drawn as two
3-vertices joined by an instantaneous line.

The initial Hamiltonian also contains counterterms (Glazek, Acta Phys. Pol. B 43, 1843 (2012), Sec. 2.4 and 3.3):
mass counterterms (a+a) and coupling constant counterterms with the same operators as the first-order terms. They are
added by add_counterterms as point-like terms.
"""
import importlib
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import factorial, prod

import numpy as np


@dataclass(frozen=True)
class Term:
    """
    order: power of the coupling constant
    legs: for every vertex, (outgoing lines per type, incoming lines per type), each a tuple of length n_types
    lines: internal lines (type, vertex a, vertex b) with a <= b, vertices numbered inside the term
    count: number of copies of the term (canonical files sometimes draw one operator several times)
    name: label used when printing products of terms
    weight: numerical factor of the operator, e.g. 1/(k! l!) for k identical creation and l identical annihilation
        operators obtained by expanding phi^4/4!
    counterterm: True for counterterms, which are drawn with a marked vertex
    """
    order: int
    legs: tuple
    lines: tuple = ()
    count: int = 1
    name: str = ""
    weight: Fraction = Fraction(1)
    counterterm: bool = False

    @property
    def n_vertices(self):
        return len(self.legs)

    def n_out(self, t):
        return sum(out[t] for out, _ in self.legs)

    def n_in(self, t):
        return sum(inc[t] for _, inc in self.legs)


@dataclass(frozen=True)
class Theory:
    """
    particle_types: names of the types of particles, in the order of the canonical diagram files
    terms: initial Hamiltonian terms
    symbols: letter of the creation and annihilation operators of each type, "" for types that are never external
        (e.g. the instantaneous lines)
    normalize: if True, every term has weight prod_t 1/(n_out_t! n_in_t!)
    """
    name: str
    particle_types: tuple
    terms: tuple
    symbols: tuple = ()
    normalize: bool = False

    @property
    def n_types(self):
        return len(self.particle_types)


def identical_particle_weight(out, inc):
    """1/(k! l!) for every type, with k creation and l annihilation operators of that type."""
    return Fraction(1, prod(factorial(k) for k in out) * prod(factorial(l) for l in inc))


def read_arrays(points, connections):
    """
    Read a diagram in the array format of rgpep_dgt/can_diagrams.

    Points that are the end of only one line are external. A line whose left end (first column) is external is an
    outgoing leg, a line whose right end (second column) is external is an incoming leg, and lines between two
    vertices are internal. Vertices are ordered by their x coordinate. A line from a vertex to itself is not a line
    but a marker of a counterterm vertex.

    Returns:
        legs: for every vertex, (outgoing lines per type, incoming lines per type)
        lines: sorted internal lines (type, vertex a, vertex b), a <= b
        marked: sorted vertices with a counterterm marker
    """
    n_types = len(connections)
    entries = [(t, int(a), int(b)) for t in range(n_types) for a, b in connections[t] if a != 0 or b != 0]
    lines = [(t, a, b) for t, a, b in entries if a != b]
    ends = Counter(v for _, a, b in lines for v in (a, b))
    internal = sorted((v for v in ends if ends[v] > 1), key=lambda v: (points[v-1][0], v))
    position = {v: k for k, v in enumerate(internal)}

    out = [[0] * n_types for _ in internal]
    inc = [[0] * n_types for _ in internal]
    internal_lines = []
    for t, a, b in lines:
        if ends[a] == 1 and ends[b] == 1:
            raise ValueError(f"line {a}-{b} is not attached to any vertex")
        if ends[a] == 1:
            out[position[b]][t] += 1
        elif ends[b] == 1:
            inc[position[a]][t] += 1
        else:
            internal_lines.append((t,) + tuple(sorted((position[a], position[b]))))

    legs = tuple((tuple(o), tuple(i)) for o, i in zip(out, inc))
    marked = sorted({position[a] for _, a, b in entries if a == b and a in position})
    return legs, tuple(sorted(internal_lines)), tuple(marked)


def term_from_arrays(points, connections, order, count=1, name=""):
    """Build a Term from a canonical diagram in the array format of rgpep_dgt/can_diagrams."""
    legs, lines, _ = read_arrays(points, connections)
    return Term(order=order, legs=legs, lines=lines, count=count, name=name)


def theory_from_canonical(name, module, particle_types, symbols, normalize=False):
    """Read the canonical diagrams (can_points, can_connections, can_count) of a module into a Theory."""
    canonical = importlib.import_module(module)
    terms = []
    for k in range(len(canonical.can_connections)):
        for j in range(len(canonical.can_connections[k])):
            count = int(np.ravel(canonical.can_count[k][j])[0])
            term = term_from_arrays(canonical.can_points[k][j], canonical.can_connections[k][j], order=k+1,
                                    count=count, name=f"H{k+1}_{j+1}")
            if normalize:
                term = _with_weight(term)
            terms.append(term)
    return Theory(name=name, particle_types=tuple(particle_types), terms=tuple(terms), symbols=tuple(symbols),
                  normalize=normalize)


def _with_weight(term):
    n_types = len(term.legs[0][0])
    out = [term.n_out(t) for t in range(n_types)]
    inc = [term.n_in(t) for t in range(n_types)]
    return Term(order=term.order, legs=term.legs, lines=term.lines, count=term.count, name=term.name,
                weight=identical_particle_weight(out, inc), counterterm=term.counterterm)


def add_counterterms(theory, max_order):
    """
    Add point-like counterterms up to max_order:
    - a mass counterterm (one creation and one annihilation operator) for every type of particle with a symbol,
    - a coupling constant counterterm with the operators of every first-order term,
    each at every order at which the theory without counterterms gives a loop correction to that operator, i.e. a
    diagram with the same external lines made of more than one term.

    The free Hamiltonian H_f never appears as a vertex in the RGPEP expansion (it only enters through the
    coefficients), so the mass counterterm is the only bilinear insertion.
    """
    from rgpep_dgt.engine.generate import generate_diagrams  # generate imports nothing from here, but keep it lazy

    structures = []  # (outgoing lines per type, incoming lines per type), name
    for t, symbol in enumerate(theory.symbols):
        if symbol:
            one = tuple(int(k == t) for k in range(theory.n_types))
            structures.append(((one, one), f"mass_{theory.particle_types[t]}"))
    for term in theory.terms:
        if term.order == 1 and not term.counterterm:
            legs = (tuple(term.n_out(t) for t in range(theory.n_types)), tuple(term.n_in(t) for t in range(theory.n_types)))
            if legs not in [s for s, _ in structures]:
                structures.append((legs, term.name))

    terms = list(theory.terms)
    for (out, inc), label in structures:
        for order in range(2, max_order + 1):
            corrections = generate_diagrams(theory, order, list(inc), list(out))
            if any(len(sequence) > 1 for diagram in corrections for sequence in diagram.products):
                weight = identical_particle_weight(out, inc) if theory.normalize else Fraction(1)
                terms.append(Term(order=order, legs=((out, inc),), name=f"CT{order}_{label}", weight=weight,
                                  counterterm=True))
    return Theory(name=theory.name, particle_types=theory.particle_types, terms=tuple(terms), symbols=theory.symbols,
                  normalize=theory.normalize)


# Theories available by name. The particle types follow the order used in the canonical diagram files. The symbols
# follow Gomez-Rocha and Glazek, PRD 92, 065005 (2015) for gluons and the comments in the QCD file (b quarks, d
# antiquarks). In phi^4 the terms come from phi^4/4!, so they get the weights 1/(k! l!).
THEORIES = {
    "phi4": dict(module="rgpep_dgt.can_diagrams.phi4.canonical_diagrams", particle_types=("phi", "unused"),
                 symbols=("a", ""), normalize=True),
    "qcd_gluons": dict(module="rgpep_dgt.can_diagrams.qcd.gluons.canonical_diagrams",
                       particle_types=("gluon", "instantaneous"), symbols=("a", "")),
    "qcd": dict(module="rgpep_dgt.can_diagrams.qcd.full_theory.canonical_diagrams",
                particle_types=("gluon", "instantaneous", "quark", "antiquark"), symbols=("a", "", "b", "d")),
}


@lru_cache(maxsize=None)
def get_theory(name, counterterms=False, max_order=None):
    """
    The theory called name. With counterterms=True the counterterms up to max_order are added (see add_counterterms).
    """
    if name not in THEORIES:
        raise ValueError(f"Unknown theory: {name}")
    theory = theory_from_canonical(name, **THEORIES[name])
    if counterterms:
        if max_order is None:
            raise ValueError("max_order is needed to add counterterms")
        theory = add_counterterms(theory, max_order)
    return theory
