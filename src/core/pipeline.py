from src.search.comparison import group_diagrams
from src.transforms.concatenation import combine_diagrams_order, return_diagram_framewok

from src.rendering.matplotlib_backend import *  # Import the file that renders the diagrams using matplotlib

def calculate_diagrams(theory, in_particles, out_particles, till_order, mode = "complete"):
    if theory == "phi4":
        # 
        from src.can_diagrams.phi4.canonical_diagrams import can_points, can_connections, can_count

    elif theory == "qcd":
        # Import the canonical diagrams for QCD
        from src.can_diagrams.qcd.full_theory.canonical_diagrams import can_points, can_connections, can_count

    elif theory == "qcd_gluons":
        # 
        from src.can_diagrams.qcd.gluons.canonical_diagrams import can_points, can_connections, can_count
        pass
    else:
        raise ValueError(f"Unknown theory: {theory}")
    
    if mode == "complete":
        all_points = [can_points[0]]
        all_connections = [can_connections[0]]
        all_count = [can_count[0]]
        for i in range(till_order-1):
            next_points, next_connections, next_count = combine_diagrams_order(all_points, all_connections, all_count, typeofproc=[in_particles, out_particles], max_order = till_order+1, theory = theory)
            next_points, next_connections, next_count = group_diagrams(next_points, next_connections, next_count)
            all_points.append(next_points)
            all_connections.append(next_connections)
            all_count.append(next_count)
        return next_points, next_connections, next_count, 0
    
    elif mode == "framework":
        in_out_init = []
        for i in range(len(can_points)):
            for j in range(len(can_points[i])):
                aux =[]
                for k in range(len(can_connections[i][j])):
                    aux.append([len(np.trim_zeros(in_out_connections(can_connections[i][j])[k][0])), 
                                        len(np.trim_zeros(in_out_connections(can_connections[i][j])[k][1]))])
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
        
        def is_array_in_list(arr, array_list):
            return any(np.array_equal(arr, existing) for existing in array_list)

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
                                points = compress_first_column(points)
                                if not is_array_in_list(points, new_points):
                                    new_points.append(points)
                                    new_paths.append(paths)
                                    new_in_out.append(in_out_array)
            all_points.append(new_points)
            all_paths.append(new_paths)
            all_in_out.append(new_in_out)
        return all_points[-1], all_paths[-1], 0, all_in_out[-1]