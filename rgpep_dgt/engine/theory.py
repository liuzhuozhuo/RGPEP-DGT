"""
Theories described as lists of initial Hamiltonian terms.

A term is a small diagram made of one or more vertices, ordered from left to right as in the product of operators.
Every vertex has external legs: outgoing legs (creation operators) and incoming legs (annihilation operators), counted
per type of particle. A term can also have internal lines between its own vertices, e.g. a quartic term drawn as two
3-vertices joined by an instantaneous line.
"""
import importlib
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

import numpy as np


@dataclass(frozen=True)
class Term:
    """
    order: power of the coupling constant
    legs: for every vertex, (outgoing lines per type, incoming lines per type), each a tuple of length n_types
    lines: internal lines (type, vertex a, vertex b) with a <= b, vertices numbered inside the term
    count: multiplicity of the term
    name: label used when printing products of terms
    """
    order: int
    legs: tuple
    lines: tuple = ()
    count: int = 1
    name: str = ""

    @property
    def n_vertices(self):
        return len(self.legs)

    def n_out(self, t):
        return sum(out[t] for out, _ in self.legs)

    def n_in(self, t):
        return sum(inc[t] for _, inc in self.legs)


@dataclass(frozen=True)
class Theory:
    name: str
    particle_types: tuple
    terms: tuple

    @property
    def n_types(self):
        return len(self.particle_types)


def term_from_arrays(points, connections, order, count=1, name=""):
    """
    Build a Term from a canonical diagram in the array format of rgpep_dgt/can_diagrams.

    Points that are the end of only one line are external. A line whose left end (first column) is external is an
    outgoing leg, a line whose right end (second column) is external is an incoming leg, and lines between two
    vertices are internal. Vertices are ordered by their x coordinate.
    """
    n_types = len(connections)
    lines = [(t, int(a), int(b)) for t in range(n_types) for a, b in connections[t] if a != 0 or b != 0]
    ends = Counter(v for _, a, b in lines for v in (a, b))
    internal = sorted((v for v in ends if ends[v] > 1), key=lambda v: (points[v-1][0], v))
    position = {v: k for k, v in enumerate(internal)}

    out = [[0] * n_types for _ in internal]
    inc = [[0] * n_types for _ in internal]
    internal_lines = []
    for t, a, b in lines:
        if ends[a] == 1 and ends[b] == 1:
            raise ValueError(f"line {a}-{b} of {name} is not attached to any vertex")
        if ends[a] == 1:
            out[position[b]][t] += 1
        elif ends[b] == 1:
            inc[position[a]][t] += 1
        else:
            internal_lines.append((t,) + tuple(sorted((position[a], position[b]))))

    legs = tuple((tuple(o), tuple(i)) for o, i in zip(out, inc))
    return Term(order=order, legs=legs, lines=tuple(sorted(internal_lines)), count=count, name=name)


def theory_from_canonical(name, module, particle_types):
    """Read the canonical diagrams (can_points, can_connections, can_count) of a module into a Theory."""
    canonical = importlib.import_module(module)
    terms = []
    for k in range(len(canonical.can_connections)):
        for j in range(len(canonical.can_connections[k])):
            count = int(np.ravel(canonical.can_count[k][j])[0])
            terms.append(term_from_arrays(canonical.can_points[k][j], canonical.can_connections[k][j], order=k+1,
                                          count=count, name=f"H{k+1}_{j+1}"))
    return Theory(name=name, particle_types=tuple(particle_types), terms=tuple(terms))


# Theories available by name. The particle types follow the order used in the canonical diagram files.
THEORIES = {
    "phi4": ("rgpep_dgt.can_diagrams.phi4.canonical_diagrams", ("phi", "unused")),
    "qcd_gluons": ("rgpep_dgt.can_diagrams.qcd.gluons.canonical_diagrams", ("gluon", "instantaneous")),
    "qcd": ("rgpep_dgt.can_diagrams.qcd.full_theory.canonical_diagrams", ("gluon", "instantaneous", "quark", "antiquark")),
}


@lru_cache(maxsize=None)
def get_theory(name):
    if name not in THEORIES:
        raise ValueError(f"Unknown theory: {name}")
    module, particle_types = THEORIES[name]
    return theory_from_canonical(name, module, particle_types)
