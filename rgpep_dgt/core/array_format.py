"""
Helpers for the array format used by the canonical diagram files and the renderer: points of dimension (P, 2) and
connections of dimension (n_types, M, 2) with 1-based point indices, padded with zeros.

These functions come unchanged from the original code, which is kept in legacy/ for reference.
"""
import numpy as np


def combine_connections(max_len = 0,*connections):
    """ 
    Combine multiple connections into a single array with the same length by padding with zeros.
    Args:
        connections (list): list of connections to combine
    Returns:
        final_connection (np.array): combined connection of dimension (len(connections), max_len, 2)
    """
    if max_len == 0:
        max_len = max([len(connection) for connection in connections])
    final_connection = np.zeros((len(connections), max_len, 2), dtype=int)
    for i in range(len(connections)):
        if len(connections[i]) < max_len:
            final_connection[i] = np.append(connections[i], np.zeros((max_len - len(connections[i]), 2), dtype=int), axis=0)
        else:
            final_connection[i] = connections[i]
    return final_connection

def trim_zeros_2D(array: np.ndarray, axis: int = 1) -> np.ndarray:
    """
    Remove any rows (axis=1) or columns (axis=0) that are entirely zero,
    even if they appear between non-zero rows/columns.
    
    Parameters
    ----------
    array : np.ndarray
        2D input array.
    axis : int, optional
        If 1 (default), drop zero-rows; if 0, drop zero-columns.
    
    Returns
    -------
    np.ndarray
        The trimmed array.
    """
    # mask[i] is True iff the i-th row/column has at least one non-zero
    mask = array.any(axis=axis)
    
    if axis:
        # drop rows where mask is False
        return array[mask, :]
    else:
        # drop columns where mask is False
        return array[:, mask]

def trim_zeros_3D(array, axis=None):
    if axis is None:
        # Trim along all axes
        mask = ~(array == 0).all(axis=(1, 2))
        trimmed_array = array[mask]

        mask = ~(trimmed_array == 0).all(axis=(0, 2))
        trimmed_array = trimmed_array[:, mask]

        mask = ~(trimmed_array == 0).all(axis=(0, 1))
        trimmed_array = trimmed_array[:, :, mask]
    elif axis == 0:
        # Trim along axis 0
        mask = ~(array == 0).all(axis=(1, 2))
        trimmed_array = array[mask]
    elif axis == 1:
        # Trim along axis 1
        mask = ~(array == 0).all(axis=(0, 2))
        trimmed_array = array[:, mask]
    elif axis == 2:
        # Trim along axis 2
        mask = ~(array == 0).all(axis=(0, 1))
        trimmed_array = array[:, :, mask]
    else:
        raise ValueError("Invalid axis. Axis must be 0, 1, 2, or None.")
    
    return trimmed_array

def prune_points_and_reindex(points, connection):
    """
    Remove all [0,0] rows from `points`, then rebuild `connection` so that:
      - any connection entry pointing to a removed point becomes 0,
      - all other entries are remapped down to a compact 1-based range.
    
    Parameters
    ----------
    points : np.ndarray, shape (N,2)
        Your (x,y) coordinates, with placeholder rows exactly equal to [0,0].
    connection : np.ndarray, shape (T,P,2), dtype=int
        Your 1-based index pairs, with [0,0] as placeholders.
    
    Returns
    -------
    new_points : np.ndarray, shape (M,2)
        The pruned points (no [0,0] rows).
    new_connection  : np.ndarray, shape (T,P,2)
        The updated connection, still 1-based with [0,0] placeholders.
    """

        # 1) Mask of rows to keep
    keep = ~(np.all(points == 0, axis=1))
    new_points = points[keep]
    
    # 2) Build old→new 1-based map
    #    new_idx[i] = new 1-based index of old row i, or 0 if dropped
    new_idx = np.zeros(points.shape[0], dtype=int)
    new_idx[keep] = np.arange(1, keep.sum()+1)
    
    # 3) Apply to connection
    #    For each entry u in connection: if u>0, replace with new_idx[u-1], else keep 0
    T, P, _ = connection.shape
    flat = connection.reshape(-1,2)
    # map both columns at once:
    mapped = np.zeros_like(flat)
    for col in (0,1):
        # grab the column, subtract 1 for 0-based indexing into new_idx
        o = flat[:,col]
        # for non-zero entries, look up new index; zeros stay zero
        mapped[:,col] = np.where(o>0, new_idx[o-1], 0)
    new_connection = mapped.reshape(T, P, 2)
    
    return new_points, new_connection

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
