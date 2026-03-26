from src.search.comparison import group_diagrams
from src.transforms.concatenation import combine_diagrams_order

def calculate_diagrams(theory, in_particles, out_particles, till_order):
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
    all_points = [can_points[0]]
    all_connections = [can_connections[0]]
    all_count = [can_count[0]]
    for i in range(till_order-1):
        next_points, next_connections, next_count = combine_diagrams_order(all_points, all_connections, all_count, typeofproc=[in_particles, out_particles], max_order = till_order+1)
        next_points, next_connections, next_count = group_diagrams(next_points, next_connections, next_count)
        all_points.append(next_points)
        all_connections.append(next_connections)
        all_count.append(next_count)
    return next_points, next_connections, next_count
