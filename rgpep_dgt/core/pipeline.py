import numpy as np

from rgpep_dgt.search.comparison import group_diagrams
from rgpep_dgt.transforms.concatenation import combine_diagrams_order, return_diagram_framewok, in_out_connections

from rgpep_dgt.rendering.matplotlib_backend import *  # Import the file that renders the diagrams using matplotlib

def calculate_diagrams(theory, in_particles, out_particles, till_order, mode = "complete", engine = "new"):
    """
    Diagrams of order till_order for a process with in_particles incoming and out_particles outgoing particles
    (numbers for each type of particle, or an int for theories with one type).

    mode = "complete" returns (points, connections, count, diagrams): every diagram with the number of Wick
        contractions that give it. With engine="new", diagrams is the list of rgpep_dgt.engine.generate.Diagram.
    mode = "framework" returns (points, paths, 0, products): the products of canonical terms that contribute,
        drawn without contractions. With engine="new", products maps each sequence of term indices to its count.

    engine = "new" uses rgpep_dgt/engine, which follows docs/literature.md and counts each contraction once.
    engine = "legacy" uses the original iterative construction, which overcounts from third order on.
    """
    if isinstance(in_particles, int):
        in_particles = [in_particles, 0]
    if isinstance(out_particles, int):
        out_particles = [out_particles, 0]

    if engine == "new":
        from rgpep_dgt.engine.theory import get_theory
        from rgpep_dgt.engine.generate import generate_diagrams, term_products
        from rgpep_dgt.engine.arrays import stack, product_to_arrays
        from rgpep_dgt.transforms.concatenation import stack_diagrams

        rgpep_theory = get_theory(theory)
        if mode == "complete":
            diagrams = generate_diagrams(rgpep_theory, till_order, in_particles, out_particles)
            points, connections, count = stack(diagrams, rgpep_theory.n_types)
            return points, connections, count, diagrams
        elif mode == "framework":
            products = term_products(rgpep_theory, till_order, in_particles, out_particles)
            points, paths, _ = stack_diagrams([product_to_arrays(rgpep_theory, sequence) + (products[sequence],)
                                               for sequence in products], rgpep_theory.n_types)
            return points, paths, 0, products
        raise ValueError(f"Unknown mode: {mode}")
    elif engine != "legacy":
        raise ValueError(f"Unknown engine: {engine}")

    if theory == "phi4":
        # 
        from rgpep_dgt.can_diagrams.phi4.canonical_diagrams import can_points, can_connections, can_count

    elif theory == "qcd":
        # Import the canonical diagrams for QCD
        from rgpep_dgt.can_diagrams.qcd.full_theory.canonical_diagrams import can_points, can_connections, can_count

    elif theory == "qcd_gluons":
        # 
        from rgpep_dgt.can_diagrams.qcd.gluons.canonical_diagrams import can_points, can_connections, can_count
        pass
    else:
        raise ValueError(f"Unknown theory: {theory}")
    
    if mode == "complete":
        all_points = [can_points[0]]
        all_connections = [can_connections[0]]
        all_count = [can_count[0]]
        next_points, next_connections, next_count = can_points[0], can_connections[0], np.ravel(can_count[0])
        for i in range(till_order-1):
            next_points, next_connections, next_count = combine_diagrams_order(all_points, all_connections, all_count, typeofproc=[in_particles, out_particles], max_order = till_order, theory = theory)
            next_points, next_connections, next_count = group_diagrams(next_points, next_connections, next_count)
            all_points.append(next_points)
            all_connections.append(next_connections)
            all_count.append(next_count)
        return next_points, next_connections, next_count, 0
    
    elif mode == "framework":
        #Only the first order canonical diagrams are used here, so the in/out lines are computed only for them
        in_out_init = []
        for j in range(len(can_points[0])):
            aux =[]
            for k in range(len(can_connections[0][j])):
                aux.append([len(np.trim_zeros(in_out_connections(can_connections[0][j])[k][0])), 
                                    len(np.trim_zeros(in_out_connections(can_connections[0][j])[k][1]))])
            in_out_init.append(aux)

        all_points = [can_points[0]]
        all_paths = [can_connections[0]]
        all_in_out = [in_out_init]

        def compress_first_column(arr):
            unique_vals = np.unique(arr[:, 0])
            
            # Build a mapping from old value -> new compressed value
            mapping = {old: new for new, old in enumerate(unique_vals)}
            
            result = arr.copy()
            result[:, 0] = np.vectorize(mapping.get)(result[:, 0])
            
            return result
        
        def is_diagram_in_list(points, paths, points_list, paths_list):
            # Diagrams with the same points can still have different lines (e.g. different types of particles)
            return any(np.array_equal(points, existing_points) and np.array_equal(paths, existing_paths)
                       for existing_points, existing_paths in zip(points_list, paths_list))

        def is_process(in_out):
            # in_out[k] = [number of incoming, number of outgoing] lines of particle type k
            for k in range(len(in_out)):
                n_in = in_particles[k] if k < len(in_particles) else 0
                n_out = out_particles[k] if k < len(out_particles) else 0
                if in_out[k][0] != n_in or in_out[k][1] != n_out:
                    return False
            return True

        for n in range (1, till_order):
            new_points = []
            new_paths = []
            new_in_out = []
            for q in range(len(all_points)):
                for p in range(len(all_points)):
                    for i in range(len(all_points[q])):
                        for j in range(len(all_points[p])):
                            if p+q+1 == n:
                                points, paths, in_out_array = return_diagram_framewok(all_points[q][i], all_paths[q][i], all_points[p][j], all_paths[p][j], all_in_out[q][i], all_in_out[p][j])
                                if len(in_out_array) == 0: # The two diagrams cannot be connected
                                    continue
                                points = compress_first_column(points)
                                if n == till_order-1:
                                    aux = any(is_process(in_out_array[k]) for k in range(len(in_out_array)))
                                    if not is_diagram_in_list(points, paths, new_points, new_paths) and aux:
                                        new_points.append(points)
                                        new_paths.append(paths)
                                        new_in_out.append(in_out_array)
                                else:
                                    if not is_diagram_in_list(points, paths, new_points, new_paths):
                                        new_points.append(points)
                                        new_paths.append(paths)
                                        new_in_out.append(in_out_array)
            all_points.append(new_points)
            all_paths.append(new_paths)
            all_in_out.append(new_in_out)
        return all_points[-1], all_paths[-1], 0, all_in_out[-1]