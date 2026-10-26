import numpy as np

from rgpep_dgt.transforms.format import trim_zeros_3D, trim_zeros_2D
from rgpep_dgt.search.comparison import unique_values
from rgpep_dgt.transforms.simplify import simplify_diagram

def in_out_connections (connections):
    max_len = max([len(path) for path in connections])
    #len(connections) is the number of type of particles
    in_out_connections = np.zeros((len(connections), 2, max_len), dtype=int)
    unique_vals = unique_values(connections.flatten())
    for i in range(len(connections)):
        inp = 0
        out = 0
        for j in range(max_len):
            if connections[i, j, 0] in unique_vals:
                in_out_connections[i, 1, out] = connections[i, j, 0]
                out += 1
            if connections[i, j, 1] in unique_vals:
                in_out_connections[i, 0, inp] = connections[i, j, 1]
                inp += 1
    in_out_connections = trim_zeros_3D(in_out_connections, axis=2)
    return in_out_connections

def how_connected(max_connections, n_connections, n_1, n_2):
    """
    Generate all possible combinations of connections between two diagrams.
    Args:
        max_connections (int): maximum number of connections between the two diagrams for each type of particle
        n_connections (int): number of connections between the two diagrams taking into account the number of types of particles
        n_1 (int): number of input for each type of particle
        n_2 (int): number of output for each type of particle
    Returns:
        combinations (np.array): array of all possible combinations of connections between the two diagrams
        of dimension (n_connections, max_connections, 2)
    """
    combinations = np.zeros((n_connections, max_connections, 2), dtype=int)
    n = 0 
    while n < n_connections:
        for j in range (n_1):
            for k in range(n_2):
                combinations[n, 0] = np.array([j+1, k+1])
                n += 1
                if n == n_connections:
                    break
            if n == n_connections:
                break
            
    n = n_1*n_2
    if max_connections >1:
        while n < n_connections:
            diff = False
            i = 1
            while i < max_connections:  
                for j in range (n_1):
                    for k in range(n_2):
                        for l in range(i):
                            if (j+1) != combinations[n, l, 0] and (k+1) != combinations[n, l, 1]:
                                diff = True
                            else:
                                diff = False
                        if diff:
                            combinations[n, i] = np.array([j+1, k+1])
                            n +=1   
                        if n == n_connections:
                            return combinations      
                i += 1
    else:
        return combinations
    
from itertools import combinations, permutations, product
def get_all_pairings(n_1, n_2):
    """
    Returns all possible connection configurations between set 1 (1..n_1)
    and set 2 (1..n_2), as an array of shape (N, min(n1,n2), 2).
    
    Each configuration is a set of k unique pairs (no element reused),
    for k from 1 to min(n_1, n_2), zero-padded to min(n_1, n_2) rows.
    """
    max_pairs = min(n_1, n_2)
    set1 = list(range(1, n_1 + 1))
    set2 = list(range(1, n_2 + 1))
    
    all_configs = []

    # k = number of active pairs in this configuration
    for k in range(1, max_pairs + 1):
        # Choose k elements from set1, then pair each permutation with k elements from set2
        for s1_combo in combinations(set1, k):
            for s2_combo in combinations(set2, k):
                for s1_perm in permutations(s1_combo):
                    # Build a zero-padded (max_pairs, 2) matrix
                    config = np.zeros((max_pairs, 2), dtype=int)
                    for i, (a, b) in enumerate(zip(s1_perm, s2_combo)):
                        config[i] = [a, b]
                    all_configs.append(config)

    return np.array(all_configs)
    
def make_connection (points1, connections1, points2, connections2, offset = 0):
    in_out_connections1 = in_out_connections(connections1)
    in_out_connections2 = in_out_connections(connections2)

    n_types = len(in_out_connections1)

    #Create the new points array
    points = np.zeros((len(points1) + len(points2), 2))
    points[:len(points1)] = points1
    points[len(points1):] = points2 + np.array([np.max(points1)+1, offset])

    #Displace the connections of the second diagram to rename the points
    for i in range(n_types):
        for j in range(len(in_out_connections2[0])):
            for k in range(len(in_out_connections2[0, 0])):
                if in_out_connections2[i, j, k] != 0:
                    in_out_connections2[i, j, k] += len(points1)

    #n1 and n2 indicate the number of input for each type of particle and output for each type of particle
    n1 = np.zeros(n_types, dtype=int)
    n2 = np.zeros(n_types, dtype=int)
    for i in range(n_types):
        n1[i] = len(np.trim_zeros(in_out_connections1[i, 0]))
        n2[i] = len(np.trim_zeros(in_out_connections2[i, 1]))

    #max_connections indicates the maximum number of connections between the two diagrams for each type of particle
    max_connections = np.zeros(n_types, dtype=int)
    for i in range(n_types):
        max_connections[i] = min(n1[i], n2[i])

    #For each type of particle, list every way of connecting its lines between the two diagrams (Wick contractions),
    #including the empty one where no line of that type is connected
    pairings_per_type = []
    for i in range(n_types):
        pairings = [np.zeros((0, 2), dtype=int)]
        if max_connections[i] > 0:
            pairings += [pairing[np.any(pairing != 0, axis=1)] for pairing in get_all_pairings(n1[i], n2[i])]
        pairings_per_type.append(pairings)

    #A combination picks one pairing for each type of particle, so any number of types can be mixed. The combination
    #where nothing is connected is dropped, since the product of two Hamiltonian terms needs at least one contraction.
    combinations = [combination for combination in product(*pairings_per_type) if any(len(pairing) for pairing in combination)]
    n_connec = len(combinations)

    #Create the connections array that will store the connections between the two diagrams.
    connections = np.zeros((n_connec, n_types, len(connections1[0]) + len(connections2[0]) + max(max_connections, default=0), 2), dtype=int)
    connections[:n_connec,:n_types,:len(connections1[0])] = connections1
    for i in range(n_connec):
        for j in range(n_types):
            for k, (in_index, out_index) in enumerate(combinations[i][j]):
                connections[i,j, len(connections1[0])+k] = np.array([in_out_connections1[j,0, in_index-1], in_out_connections2[j,1, out_index-1]])
            if (np.count_nonzero(connections2[j]) != 0):
                for k in range(len(connections2[j])):
                    if (connections2[j, k, 0] != 0 and connections2[j, k, 1] != 0):
                        connections[i,j, len(connections1[0])+max(max_connections)+k] = connections2[j, k] + np.array([len(points1), len(points1)])

    return points, connections


def matches_process(connections, typeofproc):
    """
    Check if a diagram has, for every type of particle, the number of incoming and outgoing lines asked for.
    Args:
        connections (np.array): connections of the diagram, of dimension (n_types, n_lines, 2)
        typeofproc (list): [in_particles, out_particles], each a list with the number of particles of each type.
            Types missing from the lists are taken to have 0 particles.
    Returns:
        bool: True if the diagram corresponds to the process
    """
    in_out_path = in_out_connections(connections)
    for i in range(len(connections)):
        n_in = typeofproc[0][i] if i < len(typeofproc[0]) else 0
        n_out = typeofproc[1][i] if i < len(typeofproc[1]) else 0
        if len(np.trim_zeros(in_out_path[i, 0])) != n_in or len(np.trim_zeros(in_out_path[i, 1])) != n_out:
            return False
    return True

def stack_diagrams(diagrams, n_types):
    """
    Stack a list of diagrams of different sizes into zero padded arrays.
    Args:
        diagrams (list): list of (points, connections, count)
        n_types (int): number of types of particles
    Returns:
        new_points (np.array): of dimension (N, max number of points, 2)
        new_connections (np.array): of dimension (N, n_types, max number of lines, 2)
        new_count (np.array): of dimension (N, 1)
    """
    max_points = max((len(diagram_points) for diagram_points, _, _ in diagrams), default=1)
    max_lines = max((diagram_connections.shape[1] for _, diagram_connections, _ in diagrams), default=1)
    new_points = np.zeros((len(diagrams), max_points, 2))
    new_connections = np.zeros((len(diagrams), n_types, max_lines, 2), dtype=int)
    new_count = np.zeros((len(diagrams), 1), dtype=int)
    for n, (diagram_points, diagram_connections, diagram_count) in enumerate(diagrams):
        new_points[n, :len(diagram_points)] = diagram_points
        new_connections[n, :, :diagram_connections.shape[1]] = diagram_connections
        new_count[n] = np.ravel(diagram_count)[0]
    return new_points, new_connections, new_count

def combine_diagrams_order (points, connections, count, typeofproc, max_order, offset = 0, theory = "qcd"):
    """
    Combine all the diagrams that would contribute to a give order, and type of interaction. If the order that is calculating is 
    the max_order intended, then only the diagrams of the process typeofproc are kept.
    """

    if theory == "phi4":
        # 
        from rgpep_dgt.can_diagrams.phi4.canonical_diagrams import can_points, can_connections, can_count

    elif theory == "qcd":
        # Import the canonical diagrams for QCD
        from rgpep_dgt.can_diagrams.qcd.full_theory.canonical_diagrams import can_points, can_connections, can_count

    elif theory == "qcd_gluons":
        # 
        from rgpep_dgt.can_diagrams.qcd.gluons.canonical_diagrams import can_points, can_connections, can_count
    else:
        raise ValueError(f"Unknown theory: {theory}")

    curr_order = len(points)
    n_types = len(connections[0][0])
    #Only the diagrams of the last order are filtered by process, the lower orders are needed to build the higher ones
    process = typeofproc if curr_order+1 == max_order else None

    new_diagrams = [] #List of (points, connections, count) of the new diagrams, stacked into arrays at the end

    def add_products(points1, connections1, points2, connections2, count_):
        """Add every diagram obtained by connecting diagram 1 (left) with diagram 2 (right)."""
        dummy_points, dummy_connections = make_connection(trim_zeros_2D(points1), trim_zeros_3D(connections1, axis=1), trim_zeros_2D(points2), trim_zeros_3D(connections2, axis=1), offset=offset)
        for dummy_connection in dummy_connections:
            if process is not None and not matches_process(dummy_connection, process):
                continue
            simp_points, simp_connections = simplify_diagram(dummy_points, trim_zeros_3D(dummy_connection, axis=1))
            new_diagrams.append((simp_points, simp_connections, count_))

    for i in range(len(connections[0])):
        for j in range(len(connections[-1])):
            add_products(points[-1][j], connections[-1][j], points[0][i], connections[0][i], count[0][i] * count[-1][j])
            #For curr_order = 1 the loop above already gives every ordered pair of first order diagrams,
            #so the reversed product would count each of them twice
            if curr_order > 1:
                add_products(points[0][i], connections[0][i], points[-1][j], connections[-1][j], count[0][i] * count[-1][j])
    for i in range(1, len(can_connections)):
        for j in range(i-1, len(connections)):
            if (i+1 + j) == curr_order:
                for k in range(len(can_connections[i])):
                    for l in range(len(connections[j])):
                        add_products(can_points[i][k], can_connections[i][k], points[j][l], connections[j][l], can_count[i][k] * count[j][l])
                for k in range(len(can_connections[i])):
                    for l in range(len(connections[j])):
                        add_products(points[j][l], connections[j][l], can_points[i][k], can_connections[i][k], can_count[i][k] * count[j][l])

    """for i in range(len(counter_points)):
        for j in range(i, len(connections)):
            if (i+2+ j +1) == curr_order:
                for k in range(len(counter_points[i])):
                    for l in range(len(connections[j])):
                        dummy_points, dummy_connections = make_connection(trim_zeros_2D(np.array(counter_points[i][k])), trim_zeros_3D(np.array([counter_connections[i][k],np.zeros_like(counter_connections[i][k])]), axis=1), trim_zeros_2D(points[j][l]), trim_zeros_3D(connections[j][l], axis = 1), order=curr_order, offset=offset)
                        for m in range(len(dummy_connections)):
                            if(curr_order+1  == max_order): 
                                in_out_path = in_out_connections(dummy_connections[m])
                                if (len(np.trim_zeros(in_out_path[0, 0])) != typeofproc[0][0] or len(np.trim_zeros(in_out_path[0, 1]))!= typeofproc[0][1]):
                                    continue
                            simp_points, simp_connections = simplify_diagram(dummy_points, trim_zeros_3D(dummy_connections[m], axis=1))
                            for o in range(len(simp_points)):
                                new_points[n, o] = simp_points[o]
                            for o in range(n_types):
                                for p in range(len(simp_connections[0])):
                                    new_connections[n, o, p] = simp_connections[o, p]
                            new_count[n] = can_count[i][k] * count[j][l]        
                            n += 1
                for k in range(len(counter_points[i])):
                    for l in range(len(connections[j])):
                        dummy_points, dummy_connections = make_connection(trim_zeros_2D(points[j][l]), trim_zeros_3D(connections[j][l], axis=1), trim_zeros_2D(np.array(counter_points[i][k])), trim_zeros_3D(np.array([counter_connections[i][k],np.zeros_like(counter_connections[i][k])]), axis=1), order=curr_order, offset=offset)
                        for m in range(len(dummy_connections)):
                            if(curr_order+1  == max_order): 
                                in_out_path = in_out_connections(dummy_connections[m])
                                if (len(np.trim_zeros(in_out_path[0, 0])) != typeofproc[0][0] or len(np.trim_zeros(in_out_path[0, 1]))!= typeofproc[0][1]):
                                    continue
                            simp_points, simp_connections = simplify_diagram(dummy_points, trim_zeros_3D(dummy_connections[m], axis=1))
                            for o in range(len(simp_points)):
                                new_points[n, o] = simp_points[o]
                            for o in range(n_types):
                                for p in range(len(simp_connections[0])):
                                    new_connections[n, o, p] = simp_connections[o, p]
                            new_count[n] = can_count[i][k] * count[j][l] 
                            n += 1 

                """
    #In the case of the gluon diagrams, there is only it second order diagrams, so this will only be used for curr_order = 1, but it should be general, for the cases where 
    #there are higher order canonical diagrams.
    if curr_order < len(can_connections):
        for i in range(len(can_points[curr_order])):
            if process is not None and not matches_process(can_connections[curr_order][i], process):
                continue
            new_diagrams.append((can_points[curr_order][i], can_connections[curr_order][i], can_count[curr_order][i][0]))
    
    """if curr_order < len(counter_points):
        for i in range(len(counter_points[curr_order-1])):
            for j in range(len(counter_points[curr_order-1][i])):
                new_points[n, j] = counter_points[curr_order-1][i][j]
            for j in range(n_types):
                for k in range(len(counter_connections[curr_order-1][i])):
                    if j == 0:
                        new_connections[n, j, k] = counter_connections[curr_order-1][i][k]
                    else:
                        new_connections[n, j, k] = np.zeros(2, dtype=int)
            new_count[n] = 0
            n += 1
    """
    return stack_diagrams(new_diagrams, n_types)

def equalize_x_spacing(points: np.ndarray, spacing: float = 1) -> np.ndarray:
    """
    Return a new (N×2) array where the x-coords have been remapped so that
      - each unique original x is assigned to 0, spacing, 2*spacing, … in ascending order,
      - any two points that had the same x stay tied,
      - the y-coords are left unchanged.
    
    Parameters
    ----------
    points : np.ndarray of shape (N,2)
        Your original (x,y) coordinates.
    spacing : float, default=1.0
        The distance between consecutive unique x-positions.
    
    Returns
    -------
    new_pts : np.ndarray of shape (N,2)
        The transformed points.
    """
    # 1) find the sorted unique x-values
    orig_x = points[:,0]
    uniq = np.unique(orig_x)
    
    # 2) build a map: original x → new x
    #    e.g. uniq = [1.2, 3.4, 7.9]  →  {1.2:0, 3.4:1*spacing, 7.9:2*spacing}
    mapping = {x: i * spacing for i, x in enumerate(uniq)}
    
    # 3) apply it
    new_x = np.vectorize(mapping.get)(orig_x)
    new_pts = points.copy()
    new_pts[:,0] = new_x
    return new_pts


def rearrange_in_out_points(points, connections):
    in_out_points = in_out_connections(connections)
    in_points = np.trim_zeros(in_out_points[:, 0].flatten())-1
    out_points = np.trim_zeros(in_out_points[:, 1].flatten())-1
    min_x_val = np.min(points[:, 0])
    max_x_val = np.max(points[:, 0])
    if len(out_points) > 1:
        for i in range(len(out_points)):
            if points[out_points[i], 0] == 0 and points[out_points[i], 1] == 0:
                continue
            elif points[out_points[i], 0] != min_x_val:
                equal_y = False
                for j in range(len(out_points)):
                    if points[out_points[i], 1] == points[out_points[j], 1] and i != j:
                        equal_y = True
                        break
                if equal_y:
                    points[out_points[i]] = [min_x_val, np.max(points[:, 1]) + 1]
                else:
                    points[out_points[i], 0] = min_x_val
    if len(in_points) > 1:
        for i in range(len(in_points)):
            if points[in_points[i], 0] == 0 and points[in_points[i], 1] == 0:
                continue
            elif points[in_points[i], 0] != max_x_val:
                equal_y = False
                for j in range(len(in_points)):
                    if points[in_points[i], 1] == points[in_points[j], 1] and i != j:
                        equal_y = True
                        break
                if equal_y:
                    points[in_points[i]] = [max_x_val, np.max(points[:, 1]) + 1]
                else:
                    points[in_points[i], 0] = max_x_val
    return points

from collections import defaultdict

def find_loops (points, connections, min_loop_len=3):
    edges = trim_zeros_2D(connections.reshape(-1, 2))
    graph = defaultdict(set)
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)

    cycles = set()

    def normalize(cycle):
        cycle = cycle[:-1] if cycle[0] == cycle[-1] else cycle
        n = len(cycle)
        rots = [tuple(cycle[i:] + cycle[:i]) for i in range(n)]
        rev = cycle[::-1]
        rots_rev = [tuple(rev[i:] + rev[:i]) for i in range(n)]
        return min(rots + rots_rev)

    def dfs(start, curr, path, parent):
        for nbr in graph[curr]:
            if nbr == parent:
                continue
            if nbr == start and len(path) >= min_loop_len:
                cycles.add(normalize(path))
            elif nbr not in path:
                dfs(start, nbr, path + [nbr], curr)

    for node in graph:
        dfs(node, node, [node], None)

    loops_ =  [list(c) for c in sorted(cycles)]
    if len(loops_) == 0:
        return
    else:
        max_len = max(len(l) for l in loops_)
        loops = np.full((len(loops_), max_len), 1, dtype=int)
        for i, l in enumerate(loops_):
            loops[i, :len(l)] = l
        loops = loops-1

    def other_index_out_of_loop(edges, loop, node):
        loop = set(loop)

        for a, b in edges:
            if a == node and b not in loop:
                return b
            if b == node and a not in loop:
                return a

        return None

    for loop in loops:
        loop = np.trim_zeros(loop)
        y_vals = points[loop, 1]
        if np.all(np.isclose(y_vals, y_vals[0])):
            x_pos = points[loop, 0]
            mid_vals = loop[(x_pos > x_pos.min()) & (x_pos < x_pos.max())]
            for idx in mid_vals:
                other_idx = other_index_out_of_loop(edges-1, loop, idx)
                if other_idx is not None and points[idx, 1] != points[other_idx, 1]:
                    points[idx, 1] = points[other_idx, 1]
                else:
                    points[idx, 1] += 1


def new_in_out_array(in_out_1, in_out_2):
    """
    Possible numbers of incoming and outgoing lines of each type of particle after connecting diagram 1 (left)
    with diagram 2 (right). For each type, j lines are connected, from 0 up to the number of incoming lines of
    diagram 1 or outgoing lines of diagram 2. The number is chosen independently for each type, but at least one
    line has to be connected.
    Args:
        in_out_1, in_out_2: [number of incoming, number of outgoing] lines for each type of particle
    Returns:
        new_in_out (np.array): of dimension (number of possibilities, number of types, 2)
    """
    in_out_1 = np.array(in_out_1)
    in_out_2 = np.array(in_out_2)

    ranges = [range(min(in_out_1[i][0], in_out_2[i][1]) + 1) for i in range(len(in_out_1))]
    new_in_out = []
    for j in product(*ranges):
        if sum(j) == 0:
            continue
        new_in_out.append(np.stack([in_out_1[:, 0] + in_out_2[:, 0] - np.array(j), in_out_1[:, 1] + in_out_2[:, 1] - np.array(j)], axis=1))
    return np.array(new_in_out, dtype=int).reshape(-1, len(in_out_1), 2)

def return_diagram_framewok(can_points1, can_paths1, can_points2, can_paths2, in_out1, in_out2):
    in_out1 = np.array(in_out1)
    in_out2 = np.array(in_out2)
    n1 = len(in_out1.shape)
    n2 = len(in_out2.shape)
    if n1 != 2 and n2 != 2:
        in_out_array = []
        for i in range(len(in_out1)):
            for j in range(len(in_out2)):
                aux = (new_in_out_array(in_out1[i], in_out2[j]))
                for k in range(len(aux)):
                    in_out_array.append(aux[k])
    elif n1 != 2 and n2 == 2:
        in_out_array = []
        for i in range(len(in_out1)):
            aux = (new_in_out_array(in_out1[i], in_out2))
            for k in range(len(aux)):
                in_out_array.append(aux[k])
    elif n1 == 2 and n2 != 2:
        in_out_array = []
        for i in range(len(in_out2)):
            aux = (new_in_out_array(in_out1, in_out2[i]))
            for k in range(len(aux)):
                in_out_array.append(aux[k])
    else:
        in_out_array = (new_in_out_array(in_out1, in_out2))
    #Several ways of connecting can give the same numbers of lines, keep each possibility once
    in_out_array = np.unique(np.array(in_out_array, dtype=int).reshape(-1, len(can_paths1), 2), axis=0)
    points = np.zeros((len(can_points1) + len(can_points2), 2))
    paths = np.zeros((len(can_paths1), len(can_paths1[0]) + len(can_paths2[0]), 2), dtype=int)
    points[:len(can_points1)] = can_points1
    points[len(can_points1):] = can_points2 + np.array([np.max(can_points1)+1, 0])
    paths[:len(can_paths1), :len(can_paths1[0])] = can_paths1
    for i in range(len(can_paths1)):
        for j in range(len(can_paths1[0]), len(can_paths1[0]) + len(can_paths2[0])):
            if can_paths2[i][j-len(can_paths1[0])][0] != 0 or can_paths2[i][j-len(can_paths1[0])][1] != 0:
                paths[i][j] = can_paths2[i][j-len(can_paths1[0])] + np.array([len(can_points1), len(can_points1)])

    return points, paths, in_out_array