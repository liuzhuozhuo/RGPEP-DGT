"""
Export of diagrams of rgpep_dgt.engine as TikZ-Feynman code and as a LaTeX document with their expressions.

The document needs the tikz-feynman package and compiles with pdflatex, since the vertices are placed explicitly.
External particles are labelled as in rgpep_dgt.engine.expressions.external_legs: outgoing ones (on the left) first.
Counterterm vertices are drawn as crossed dots.
"""
from collections import Counter

import numpy as np

from rgpep_dgt.engine.arrays import diagram_to_arrays
from rgpep_dgt.engine.expressions import diagram_expression, external_legs, products_table

# TikZ-Feynman style of each type of particle. Lines are written from left to right, and particles go from the right
# (annihilated) to the left (created), so quarks have their arrow pointing left.
LINE_STYLES = {
    "phi": "plain",
    "gluon": "gluon",
    "instantaneous": "ghost",
    "quark": "anti fermion",
    "antiquark": "fermion",
}

X_SCALE = 1.6
Y_SCALE = 0.8


def diagram_tikz(theory, diagram, labels=True):
    """TikZ-Feynman code of one diagram."""
    points, connections = diagram_to_arrays(diagram, theory.n_types)
    n_vertices = diagram.n_vertices
    legs = external_legs(diagram)

    lines = ["\\begin{tikzpicture}[baseline=(current bounding box.center)]", "\\begin{feynman}"]
    for v in range(n_vertices):
        style = "[crossed dot] " if v in diagram.counterterms else ("[dot] " if n_vertices > 1 else "")
        x, y = points[v]
        lines.append(f"  \\vertex {style}(v{v + 1}) at ({x * X_SCALE:.2f}, {y * Y_SCALE:.2f}) {{}};")
    # The external points of diagram_to_arrays follow the order of external_legs
    for label, _, _, _ in legs:
        x, y = points[n_vertices + label - 1]
        text = f"{{\\({label}\\)}}" if labels else "{}"
        lines.append(f"  \\vertex (e{label}) at ({x * X_SCALE:.2f}, {y * Y_SCALE:.2f}) {text};")

    def name(p):
        return f"v{p}" if p <= n_vertices else f"e{p - n_vertices}"

    edges = []
    for t in range(theory.n_types):
        pairs = Counter((int(a), int(b)) for a, b in connections[t] if a != 0 and a != b)
        style = LINE_STYLES.get(theory.particle_types[t], "plain")
        for (a, b), m in sorted(pairs.items()):
            # Several lines between the same points are bent symmetrically
            for bend in (np.linspace(-35, 35, m) if m > 1 else [0]):
                bend_style = "" if bend == 0 else (f", bend left={bend:.0f}" if bend > 0 else f", bend right={-bend:.0f}")
                edges.append(f"    ({name(a)}) -- [{style}{bend_style}] ({name(b)})")
    lines += ["  \\diagram* {", ",\n".join(edges), "  };", "\\end{feynman}", "\\end{tikzpicture}"]
    return "\n".join(lines)


def latex_document(theory, diagrams, title="", products=None):
    """
    A standalone LaTeX document with every diagram and its expression, and optionally the table of products of
    terms (e.g. from term_products).
    """
    body = ["\\documentclass[a4paper]{article}",
            "\\usepackage[margin=2cm]{geometry}",
            "\\usepackage{amsmath}",
            "\\usepackage[compat=1.1.0]{tikz-feynman}",
            "\\begin{document}"]
    if title:
        body.append(f"\\section*{{{title}}}")
    if products is not None:
        body += ["\\subsection*{Products of terms}", "\\begin{verbatim}", products_table(theory, products),
                 "\\end{verbatim}"]
    body.append("\\subsection*{Diagrams}")
    for k, diagram in enumerate(diagrams):
        expression = diagram_expression(theory, diagram, latex=True, per_line=3)
        # Long expressions are broken into lines (multline), short ones stay centred on one line
        environment = "multline*" if "\\\\" in expression else "equation*"
        body += [f"\\paragraph{{{k + 1}.}}", "\\begin{center}", diagram_tikz(theory, diagram), "\\end{center}",
                 f"\\begin{{{environment}}}", expression, f"\\end{{{environment}}}"]
    body.append("\\end{document}")
    return "\n".join(body) + "\n"


def write_latex(path, theory, diagrams, title="", products=None):
    """Write latex_document to path."""
    with open(path, "w") as f:
        f.write(latex_document(theory, diagrams, title=title, products=products))
