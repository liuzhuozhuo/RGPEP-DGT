import numpy as np

def unique_values(array):
    unique, counts = np.unique(array, return_counts=True)
    unique_values = unique[counts == 1]
    return unique_values

def find_equal_subarrays(array):
    """"
    Find the positions of duplicate subarrays in a 2D array. Used mainly for detecting duplicate connections,
    which indicate the presence of a 2-loop structure in the diagram.
    Args:
        array (np.array): 2D array to search for duplicates
    Returns:
        duplicate_positions (list): list of positions of duplicate
    """
    sorted_subarrays = [np.sort(subarray) for subarray in array]
    unique_subarrays, indices, counts = np.unique(sorted_subarrays, axis=0, return_index=True, return_counts=True)
    duplicate_positions = [np.where((sorted_subarrays == unique_subarrays[i]).all(axis=1))[0] for i in range(len(unique_subarrays)) if counts[i] > 1]
    return duplicate_positions

def find_equal_subarrays_3D(array, padding_value=0):
    """"
    Find the positions of duplicate subarrays in a 3D array. Used mainly for detecting duplicate connections,
    which indicate the presence of a 2-loop structure in the diagram.
    Args:
        array (np.array): 3D array to search for duplicates
    Returns:
        duplicate_positions (list): list of positions of duplicate
    """
    array = np.array(array)

    all_rows = []
    positions = []
    for i, subarray in enumerate(array):
        for j, row in enumerate(subarray):
            if np.all(row == padding_value):
                continue
            all_rows.append(np.sort(row))
            positions.append((i, j))

    all_rows = np.array(all_rows)
    unique_rows, indices, counts = np.unique(all_rows, axis=0, return_index=True, return_counts=True)

    duplicate_positions = {}
    for k in range(len(unique_rows)):
        if counts[k] > 1:
            matches = np.where((all_rows == unique_rows[k]).all(axis=1))[0]
            key = tuple(unique_rows[k])  # e.g. (2, 3) as dict key
            duplicate_positions[key] = [positions[m] for m in matches]

    return duplicate_positions

def diagram_signature(points: np.ndarray, paths: np.ndarray) -> tuple:
    """
    Signature that does not depend on how the points of a diagram are numbered, so that diagrams that only differ by
    the numbering of their points (or by the y coordinates used for drawing) get the same signature.

    Internal vertices are labelled by the rank of their x coordinate, which is their position in the product of
    Hamiltonian terms. External points (the ones that appear in only one line) are labelled only by being
    incoming (right end of a line) or outgoing (left end of a line). If two internal vertices share an x coordinate
    their own index is kept, which can only stop equal diagrams from being grouped, never group different ones.

    points: (P, 2)
    paths: (K, M, 2)
    returns: sorted tuple of (type of particle, label of one end, label of the other end) for every line
    """
    lines = [(k, int(a), int(b)) for k in range(len(paths)) for a, b in paths[k] if a != 0 or b != 0]
    ends = [a for _, a, _ in lines] + [b for _, _, b in lines]
    values, counts = np.unique(ends, return_counts=True)
    external = set(values[counts == 1].tolist())

    internal = sorted(set(ends) - external)
    x_internal = [points[v-1, 0] for v in internal]
    x_ranks = {x: rank for rank, x in enumerate(sorted(set(x_internal)))}
    label = {}
    for v, x in zip(internal, x_internal):
        tied = x_internal.count(x) > 1
        label[v] = (0, x_ranks[x], v if tied else 0)

    def end_label(v, is_right_end):
        if v in external:
            return (1, 0 if is_right_end else 1, 0) # (1, 0, 0) incoming, (1, 1, 0) outgoing
        return label[v]

    sig = [(k,) + tuple(sorted((end_label(a, False), end_label(b, True)))) for k, a, b in lines]
    return tuple(sorted(sig))

#From Chatgpt
def group_diagrams(points: np.ndarray,
                   paths: np.ndarray,
                   numbers: np.ndarray):
    """
    points:  (N, P, 2)
    paths:   (N, K, M, 2)
    numbers: (N, 1)
    """
    # 1) filter out the “all-zero” diagrams in one vectorized mask
    nonzero_mask = ~((paths == 0).all(axis=(1,2,3)))
    pts  = points [nonzero_mask]
    pths = paths  [nonzero_mask]
    nums = numbers[nonzero_mask, 0]

    if len(pts) == 0:
        return pts, pths, nums

    # 2) single-pass grouping via a dict
    sig2group = {}
    grouped_pts  = []
    grouped_pths = []
    counts       = []

    for idx, (pt, pth, num) in enumerate(zip(pts, pths, nums)):
        sig = diagram_signature(pt, pth)
        if sig in sig2group:
            gi = sig2group[sig]
            counts[gi] += num
        else:
            gi = len(grouped_pts)
            sig2group[sig] = gi
            grouped_pts .append(pt)
            grouped_pths.append(pth)
            counts    .append(num)

    # 3) stack into arrays
    G = len(grouped_pts)
    grouped_points = np.stack(grouped_pts, axis=0)   # (G, P, 2)
    grouped_paths  = np.stack(grouped_pths, axis=0)  # (G, K, M, 2)
    counts         = np.array(counts)                # (G,)

    return grouped_points, grouped_paths, counts