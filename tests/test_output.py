"""Expressions, tables and LaTeX/TikZ output."""
import shutil
import subprocess
from itertools import combinations

import pytest

from rgpep_dgt import generate_diagrams, get_theory, term_products
from rgpep_dgt.engine.expressions import (coefficient_label, diagram_expression, external_legs, products_table)
from rgpep_dgt.engine.generate import bracketings
from rgpep_dgt.rendering.tikz import diagram_tikz, latex_document


def all_pairs(n):
    return frozenset(combinations(range(n), 2))


def test_coefficient_labels_of_third_order_follow_glazek():
    # Glazek, Acta Phys. Pol. B 43, 1843 (2012), Eq. (31) and (B.13), (B.14)
    assert {coefficient_label(tree) for tree in bracketings(3, all_pairs(3))} == {"(124,(234,0))", "(134,(123,0))"}


def test_coefficient_labels_of_fourth_order_follow_glazek():
    # The five coefficients of G04axyzb in Eq. (32), defined in (B.15)-(B.19)
    assert {coefficient_label(tree) for tree in bracketings(4, all_pairs(4))} == {
        "(125,(235,(345,0)))", "(125,(245,(234,0)))", "(145,(124,(234,0)))", "(145,(134,(123,0)))",
        "(135,(123,0),(345,0))"}


def test_second_order_and_single_term_labels():
    assert coefficient_label((0, 1)) == "(123,0)"  # (B.12)
    assert coefficient_label(0) == "0"


def test_sunset_expression():
    theory = get_theory("phi4")
    (sunset,) = generate_diagrams(theory, 2, 1, 1)
    # (a+aaa)(a+a+a+a) with weight 3! / (3! 3!) = 1/6
    assert diagram_expression(theory, sunset) == "f_t B(123,0) 1/6 (H1_3 H1_2) -> a†1 a2"


def test_vertex_counterterm_expression_has_no_coefficient():
    theory = get_theory("qcd_gluons", True, 3)
    expressions = [diagram_expression(theory, d) for d in generate_diagrams(theory, 3, [1, 0], [2, 0])]
    assert "f_t 1 (CT3_H1_1) -> a†1 a†2 a3" in expressions


def test_external_labels_outgoing_first():
    theory = get_theory("qcd")
    for diagram in generate_diagrams(theory, 3, [0, 0, 1, 0], [1, 0, 1, 0]):
        legs = external_legs(diagram)
        assert [label for label, *_ in legs] == [1, 2, 3]
        assert [io for *_, io in legs] == ["out", "out", "in"]


def test_products_table_lists_operators():
    theory = get_theory("qcd")
    table = products_table(theory, term_products(theory, 2, [1, 0, 0, 0], [1, 0, 0, 0]))
    assert table.splitlines() == ["2  H1_2 · H1_1  (a†aa)(a†a†a)", "1  H1_8 · H1_7  (a†bd)(b†d†a)"]


def test_tikz_marks_counterterms_and_bends_parallel_lines():
    theory = get_theory("phi4", True, 2)
    diagrams = generate_diagrams(theory, 2, 2, 2)
    code = "\n".join(diagram_tikz(theory, d) for d in diagrams)
    assert code.count("crossed dot") == 1        # the coupling counterterm
    assert "bend left=35" in code and "bend right=35" in code  # the two lines of the bubble


@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex is not installed")
def test_latex_document_compiles(tmp_path):
    theory = get_theory("qcd_gluons", True, 3)
    diagrams = generate_diagrams(theory, 3, [1, 0], [2, 0])
    tex = tmp_path / "diagrams.tex"
    tex.write_text(latex_document(theory, diagrams, title="test", products=term_products(theory, 3, [1, 0], [2, 0])))
    result = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name], cwd=tmp_path,
                            capture_output=True, text=True, timeout=120)
    if "tikz-feynman.sty' not found" in result.stdout:
        pytest.skip("tikz-feynman is not installed")
    assert result.returncode == 0, result.stdout[-2000:]
    assert (tmp_path / "diagrams.pdf").exists()
