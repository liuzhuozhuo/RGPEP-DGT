"""
Readable output of the diagrams: the operators of terms and diagrams, and the RGPEP coefficient of every diagram.

Every diagram of order n is a term of the effective Hamiltonian H_tn,
    f_t [sum over bracketings of B_t^(...)] x (weight) x (product of initial terms)  ->  external operators,
where f_t is the form factor and B_t^(...) are the coefficients of Glazek, Acta Phys. Pol. B 43, 1843 (2012),
Eqs. (B.12)-(B.19). Configurations are numbered 1, 2, ..., n+1 from left to right around the n factors. A product of
two groups of factors spanning configurations i..k with the split at j gives A_{ijk} in the integrand; the label of
the coefficient lists (ijk, labels of the groups with more than one factor), and 0 when both groups are single factors.
For example the bracketing (0, (1, 2)) gives B^(124,(234,0)) and ((0, 1), (2, 3)) gives B^(135,(123,0),(345,0)).
"""
from fractions import Fraction
from math import prod


def _span(tree):
    """First and one-past-last factor of a bracketing tree."""
    if isinstance(tree, int):
        return tree, tree + 1
    return _span(tree[0])[0], _span(tree[1])[1]


def coefficient_label(tree):
    """Label of the RGPEP coefficient B of a bracketing tree, e.g. "(124,(234,0))". A single factor gives "0"."""
    if isinstance(tree, int):
        return "0"
    lo, split = _span(tree[0])
    hi = _span(tree[1])[1]
    configurations = (lo + 1, split + 1, hi + 1)
    separator = "" if hi + 1 < 10 else "."
    inner = [coefficient_label(sub) for sub in tree if not isinstance(sub, int)]
    return "(" + separator.join(map(str, configurations)) + "," + ",".join(inner or ["0"]) + ")"


def operator_string(theory, out, inc, labels=None, latex=False):
    """
    Normal-ordered product of creation (out) and annihilation (inc) operators, with out and inc the numbers of
    operators of each type. labels, if given, are the labels of the operators in the same order.
    """
    operators = []
    for counts, dagger in ((out, True), (inc, False)):
        for t, n in enumerate(counts):
            operators += [(theory.symbols[t] or theory.particle_types[t], dagger)] * n
    if labels is None:
        labels = [""] * len(operators)
    text = []
    for (symbol, dagger), label in zip(operators, labels):
        if latex:
            text.append(symbol + ("^\\dagger" if dagger else "") + (f"_{{{label}}}" if label != "" else ""))
        else:
            text.append(symbol + ("†" if dagger else "") + str(label))
    # Labelled operators are separated by spaces (a†1 a2), unlabelled ones are written together (a†aa)
    return " ".join(text) if latex or any(labels) else "".join(text)


def term_operator(theory, term, latex=False):
    """Operators of a term, e.g. a†a†a."""
    out = [term.n_out(t) for t in range(theory.n_types)]
    inc = [term.n_in(t) for t in range(theory.n_types)]
    return operator_string(theory, out, inc, latex=latex)


def external_legs(diagram):
    """
    External lines of a diagram as (label, vertex, type, "out" or "in"). Outgoing lines are numbered first, from 1,
    then incoming ones, both in the order of their vertices (and type).
    """
    legs = []
    for direction in ("out", "in"):
        for v, t, io, n in sorted(diagram.external, key=lambda e: (e[0], e[1])):
            if io == direction:
                legs += [(v, t, io)] * n
    return [(k + 1, v, t, io) for k, (v, t, io) in enumerate(legs)]


def diagram_operator(theory, diagram, latex=False):
    """External operators of a diagram with their labels, e.g. a†1 a†2 a3."""
    legs = external_legs(diagram)
    out = [sum(1 for _, _, t, io in legs if t == s and io == "out") for s in range(theory.n_types)]
    inc = [sum(1 for _, _, t, io in legs if t == s and io == "in") for s in range(theory.n_types)]
    labels = [label for label, _, t, io in sorted(legs, key=lambda l: (l[3] != "out", l[2], l[0]))]
    return operator_string(theory, out, inc, labels=labels, latex=latex)


def _term_name(term, latex):
    return f"\\mathrm{{{term.name}}}".replace("_", "\\_") if latex else term.name


def _number(x, latex):
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    return f"\\tfrac{{{x.numerator}}}{{{x.denominator}}}" if latex else f"{x.numerator}/{x.denominator}"


def diagram_expression(theory, diagram, latex=False):
    """
    The diagram as a term of the effective Hamiltonian, e.g.
        f_t [B(124,(234,0)) + B(134,(123,0))] 36 (H1_3 H1_1 H1_2) -> a†1 a2
    The number in front of each product is its weight (its count when the terms have no normalisation).
    """
    trees = diagram.bracketings
    if latex:
        coefficients = [f"\\mathcal{{B}}_t^{{{coefficient_label(tree)}}}" for tree in trees if not isinstance(tree, int)]
    else:
        coefficients = [f"B{coefficient_label(tree)}" for tree in trees if not isinstance(tree, int)]
    if not coefficients:
        coefficient = ""
    elif len(coefficients) == 1:
        coefficient = coefficients[0]
    else:
        coefficient = ("\\left[" if latex else "[") + " + ".join(coefficients) + ("\\right]" if latex else "]")

    products = []
    for sequence, count in diagram.products.items():
        weight = count * prod((theory.terms[i].weight for i in sequence), start=Fraction(1))
        names = (" " if not latex else "\\, ").join(_term_name(theory.terms[i], latex) for i in sequence)
        products.append(f"{_number(weight, latex)}" + ("\\," if latex else " ") +
                        ("\\left(" if latex else "(") + names + ("\\right)" if latex else ")"))
    product_text = products[0] if len(products) == 1 else \
        ("\\left[" if latex else "[") + " + ".join(products) + ("\\right]" if latex else "]")

    form_factor = "f_t" if latex else "f_t"
    parts = [form_factor] + ([coefficient] if coefficient else []) + [product_text]
    arrow = "\\;\\to\\;" if latex else " -> "
    return (" " if not latex else "\\, ").join(parts) + arrow + diagram_operator(theory, diagram, latex=latex)


def expression_table(theory, diagrams):
    """One line per diagram with its expression."""
    width = len(str(len(diagrams)))
    return "\n".join(f"{k + 1:>{width}}. {diagram_expression(theory, d)}" for k, d in enumerate(diagrams))


def products_table(theory, products):
    """
    The products of terms before contraction (e.g. from term_products), one per line, with their total count and
    the operators of every term.
    """
    lines = []
    for sequence, count in products.items():
        names = " · ".join(theory.terms[i].name for i in sequence)
        operators = "".join(f"({term_operator(theory, theory.terms[i])})" for i in sequence)
        lines.append((str(count), names, operators))
    widths = [max((len(line[k]) for line in lines), default=0) for k in range(2)]
    return "\n".join(f"{c:>{widths[0]}}  {n:<{widths[1]}}  {o}" for c, n, o in lines)
