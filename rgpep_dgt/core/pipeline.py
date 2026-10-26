from rgpep_dgt.core.array_format import stack_diagrams
from rgpep_dgt.engine.arrays import product_to_arrays, stack
from rgpep_dgt.engine.generate import generate_diagrams, term_products
from rgpep_dgt.engine.theory import get_theory

from rgpep_dgt.rendering.matplotlib_backend import *  # Import the file that renders the diagrams using matplotlib

def calculate_diagrams(theory, in_particles, out_particles, till_order, mode = "complete", counterterms = False,
                       workers = 1, cache = False):
    """
    Diagrams of order till_order for a process with in_particles incoming and out_particles outgoing particles
    (numbers for each type of particle, or an int for theories with one type).

    mode = "complete" returns (points, connections, count, diagrams): every diagram with the number of Wick
        contractions that give it, and the list of rgpep_dgt.engine.generate.Diagram.
    mode = "framework" returns (points, paths, 0, products): the products of canonical terms that contribute,
        drawn without contractions, and a dict mapping each sequence of term indices to its count.

    counterterms = True adds mass and coupling constant counterterms to the theory, see
        rgpep_dgt.engine.theory.add_counterterms.
    workers = number of processes (None for one per CPU) and cache = True to keep results on disk, see
        rgpep_dgt.engine.generate.generate_diagrams. Both only pay off for large orders.

    The original algorithm is kept in legacy/pipeline.py for comparison.
    """
    if isinstance(in_particles, int):
        in_particles = [in_particles, 0]
    if isinstance(out_particles, int):
        out_particles = [out_particles, 0]

    rgpep_theory = get_theory(theory, counterterms, till_order if counterterms else None)
    if mode == "complete":
        diagrams = generate_diagrams(rgpep_theory, till_order, in_particles, out_particles, workers=workers, cache=cache)
        points, connections, count = stack(diagrams, rgpep_theory.n_types)
        return points, connections, count, diagrams
    elif mode == "framework":
        products = term_products(rgpep_theory, till_order, in_particles, out_particles, workers=workers, cache=cache)
        points, paths, _ = stack_diagrams([product_to_arrays(rgpep_theory, sequence) + (products[sequence],)
                                           for sequence in products], rgpep_theory.n_types)
        return points, paths, 0, products
    raise ValueError(f"Unknown mode: {mode}")
