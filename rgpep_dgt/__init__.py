__version__ = "0.0.1"

from rgpep_dgt.core.pipeline import calculate_diagrams
from rgpep_dgt.engine.expressions import diagram_expression, expression_table, products_table
from rgpep_dgt.engine.generate import Diagram, generate_diagrams, term_products
from rgpep_dgt.engine.theory import Term, Theory, get_theory
from rgpep_dgt.rendering.matplotlib_backend import represent_order_diagram
from rgpep_dgt.rendering.tikz import diagram_tikz, latex_document, write_latex

__all__ = [
    "calculate_diagrams",
    "represent_order_diagram",
    "get_theory",
    "generate_diagrams",
    "term_products",
    "diagram_expression",
    "expression_table",
    "products_table",
    "diagram_tikz",
    "latex_document",
    "write_latex",
    "Theory",
    "Term",
    "Diagram",
]
