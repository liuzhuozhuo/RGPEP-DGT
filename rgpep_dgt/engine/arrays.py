"""
Conversion between the diagrams of rgpep_dgt/engine and the arrays used by the rest of the code (points of dimension
(P, 2) and connections of dimension (n_types, M, 2) with 1-based point indices), so that the renderer can be used.
"""
from collections import Counter

import numpy as np

from rgpep_dgt.engine.theory import read_arrays
from rgpep_dgt.transforms.concatenation import stack_diagrams


def layout(n_vertices, lines, external, n_types, counterterms=()):
    """
    Points and connections of a diagram. Vertex k is drawn at x = k + 1. Outgoing external points are at x = 0 and
    incoming ones at x = n_vertices + 1, spread in y. A vertex is drawn at the mean height of its external points.

    lines: list of (type, vertex a, vertex b), one entry per line
    external: list of (vertex, type, "out" or "in"), one entry per external line
    counterterms: vertices that are counterterms, marked by a line from the vertex to itself in the first type,
        which the renderer draws as a dot
    """
    n_out = sum(1 for _, _, io in external if io == "out")
    n_in = len(external) - n_out
    height = max(n_out, n_in, 1)

    points = [[k + 1, 0.0] for k in range(n_vertices)]
    vertex_heights = [[] for _ in range(n_vertices)]
    connections = [[] for _ in range(n_types)]
    placed = Counter()
    for v, t, io in sorted(external, key=lambda e: (e[2] == "in", e[0], e[1])):
        side_total = n_out if io == "out" else n_in
        y = 1 + 2 * placed[io] + (height - side_total)  # centre the shorter side
        placed[io] += 1
        points.append([0 if io == "out" else n_vertices + 1, y])
        vertex_heights[v].append(y)
        p = len(points)
        connections[t].append([p, v + 1] if io == "out" else [v + 1, p])
    for k in range(n_vertices):
        points[k][1] = float(np.mean(vertex_heights[k])) if vertex_heights[k] else float(height)
    for t, a, b in lines:
        connections[t].append([a + 1, b + 1])
    for v in counterterms:
        connections[0].append([v + 1, v + 1])

    max_lines = max(len(c) for c in connections)
    array = np.zeros((n_types, max(max_lines, 1), 2), dtype=int)
    for t, c in enumerate(connections):
        if c:
            array[t, :len(c)] = c
    return np.array(points, dtype=float), array


def diagram_to_arrays(diagram, n_types):
    lines = [(t, a, b) for t, a, b, m in diagram.lines for _ in range(m)]
    external = [(v, t, io) for v, t, io, n in diagram.external for _ in range(n)]
    return layout(diagram.n_vertices, lines, external, n_types, diagram.counterterms)


def product_to_arrays(theory, sequence):
    """A product of terms drawn without contractions, every leg external."""
    terms = [theory.terms[i] for i in sequence]
    offsets = [sum(term.n_vertices for term in terms[:f]) for f in range(len(terms))]
    lines = [(t, a + offsets[f], b + offsets[f]) for f, term in enumerate(terms) for t, a, b in term.lines]
    external = []
    for f, term in enumerate(terms):
        for k, (out, inc) in enumerate(term.legs):
            for t in range(theory.n_types):
                external += [(offsets[f] + k, t, "out")] * out[t] + [(offsets[f] + k, t, "in")] * inc[t]
    counterterms = [offsets[f] + k for f, term in enumerate(terms) if term.counterterm for k in range(term.n_vertices)]
    return layout(offsets[-1] + terms[-1].n_vertices, lines, external, theory.n_types, counterterms)


def stack(diagrams, n_types):
    """Arrays of points (N, P, 2), connections (N, n_types, M, 2) and counts (N,) of a list of diagrams."""
    points, connections, count = stack_diagrams(
        [diagram_to_arrays(d, n_types) + (d.count,) for d in diagrams], n_types)
    return points, connections, count.ravel()


def key_from_arrays(points, connections):
    """The key of rgpep_dgt.engine.generate.Diagram for a diagram given as arrays."""
    legs, internal_lines, marked = read_arrays(points, connections)
    lines = Counter(internal_lines)
    external = [(v, t, "out", out[t]) for v, (out, _) in enumerate(legs) for t in range(len(out)) if out[t]]
    external += [(v, t, "in", inc[t]) for v, (_, inc) in enumerate(legs) for t in range(len(inc)) if inc[t]]
    return (len(legs), tuple(sorted((t, a, b, m) for (t, a, b), m in lines.items())), tuple(sorted(external)),
            marked)
