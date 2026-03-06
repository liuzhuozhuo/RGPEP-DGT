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

def diagram_signature(paths: np.ndarray) -> tuple:
    """
    paths: (K, M, 2)
    returns: a tuple of length K, where each element is
             a flattened tuple of that row's points sorted lexicographically.
    """
    sig = []
    for row in paths:
        # sort points by (x, then y)
        idx = np.lexsort((row[:,1], row[:,0]))
        sorted_row = row[idx]
        sig.append(tuple(sorted_row.ravel()))
    return tuple(sig)

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

    # 2) single-pass grouping via a dict
    sig2group = {}
    grouped_pts  = []
    grouped_pths = []
    counts       = []

    for idx, (pt, pth, num) in enumerate(zip(pts, pths, nums)):
        sig = diagram_signature(pth)
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