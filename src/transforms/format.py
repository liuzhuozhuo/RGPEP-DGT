import numpy as np
from collections import deque

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

#From chatgpt 
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
    
#From chatgpt 
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

def detect_3p_loops(points, paths):
    """
    
    """
    loop = np.zeros((len(paths), int(len(trim_zeros_2D(paths[0]))/3), 3), dtype=int)
    n = 0
    for i in range(len(paths)):
        if np.count_nonzero(paths[i]) == 0:
            continue
        path = trim_zeros_2D(paths[i])
        if (len(path) < 3):
            continue
        index = np.arange(len(path))
        j = 0
        for j in range(len(path)):
            if j in index:
                start = path[j, 0]
                end = path[j, 1]
                next = -1
                for k in range(len(path)):
                    if(k != j and k in index):
                        if path[k, 0] == start:
                            next = path[k, 1]
                        elif path[k, 1] == start:
                            next = path[k, 0]
                        if next == -1:
                            continue
                        for l in range(len(path)):
                            next2 = -1
                            if (l != j and l!= k and l in index):
                                if path[l, 0] == next:
                                    next2 = path[l, 1]
                                elif path[l, 1] == next:
                                    next2 = path[l, 0]
                                if next2 == next:
                                    continue
                                if next2 == end:
                                    loop[i, n, 0] = j+1
                                    loop[i, n, 1] = k+1
                                    loop[i, n, 2] = l+1
                                    index = np.delete(index, np.where(index == j))
                                    index = np.delete(index, np.where(index == k))
                                    index = np.delete(index, np.where(index == l))

    return trim_zeros_3D(loop, axis=0)

def detect_superposition(points, paths):
    loop = detect_3p_loops(points, paths)
    if np.count_nonzero(loop) == 0:
        return points, paths  
    else:
        for i in range(len(loop)):
            if np.count_nonzero(loop[i]) == 0:
                continue
            for j in range(len(loop[i])):
                if np.count_nonzero(loop[i, j]) == 0:
                    continue
                else:
                    height = points[paths[i,loop[i, j, 0]-1, 0]-1, 1]
                    sorted_array = sorted([paths[i,loop[i, j, 0]-1, 0], paths[i,loop[i, j, 1]-1, 0], paths[i,loop[i, j, 2]-1, 0], paths[i,loop[i, j, 0]-1, 1], paths[i,loop[i, j, 1]-1, 1], paths[i,loop[i, j, 2]-1, 1]])
                    same_height = True
                    for k in sorted_array:
                        if points[k-1, 1] != height:
                            same_height = False
                            break
                    if same_height:
                        middle = sorted_array[2]-1
                        points[middle, 1] = height+1
                    else:
                        continue
        return points, paths
    
#From Chatgpt
def equalize_x_spacing(points: np.ndarray, spacing: float = 1.0) -> np.ndarray:
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

#From Chatgpt
def find_same_height_outside(points: np.ndarray, route_ids: list[int]) -> list[int]:
    """
    Given:
      - points:  (N,2) array of (x,y) coords, zero-based indexing
      - route_ids: list of 1-based point IDs (from your path), all sharing the same y
    Returns:
      - list of 1-based IDs of all other points whose y == that common y
    """
    # convert to zero-based indices
    idxs = [rid - 1 for rid in route_ids]
    y_route = points[idxs, 1]
    if not np.allclose(y_route, y_route[0]):
        raise ValueError(f"Route points do not share one y: {y_route}")
    y0 = y_route[0]

    # mask all points at that y, then exclude route indices
    same_y = np.isclose(points[:, 1], y0)
    mask = same_y.copy()
    mask[idxs] = False

    outside_idxs = np.nonzero(mask)[0]
    # convert back to 1-based IDs
    return (outside_idxs + 1).tolist()

#From Chatgpt
def find_shortest_undirected_path(paths: np.ndarray, start: int, end: int):
    """
    Given:
      - paths: array of shape (T, P, 2), listing edges [u, v]
      - start: starting node
      - end:   target node
    Returns:
      - (num_hops, path_nodes)
        * num_hops: minimum number of edges
        * path_nodes: list of nodes [start, ..., end]
    Raises:
      ValueError if no route exists.
    """
    # 1) Build adjacency lists, preserving your input order
    adj = {}  # node -> list of neighbors in the order encountered
    T, P, _ = paths.shape
    for t in range(T):
        for p in range(P):
            u, v = int(paths[t, p, 0]), int(paths[t, p, 1])
            # skip placeholders or self‐loops
            if u == v or (u == 0 and v == 0):
                continue
            adj.setdefault(u, []).append(v)
            adj.setdefault(v, []).append(u)

    # 2) BFS to find shortest path
    visited = {start}
    queue = deque([(start, [start])])  # (current_node, path_so_far)
    while queue:
        node, path = queue.popleft()
        # explore neighbors in **exact** order they were added
        for nbr in adj.get(node, []):
            if nbr in visited:
                continue
            new_path = path + [nbr]
            if nbr == end:
                return len(new_path) - 1, new_path
            visited.add(nbr)
            queue.append((nbr, new_path))

    raise ValueError(f"No path found from {start} to {end}")

#From Chatgpt
def is_ordered_route(route):
    """
    Return True if `route` is strictly monotonic (either all increasing or all decreasing).
    Examples:
      [1, 3, 4, 5] → True (increasing)
      [6, 5, 3, 2] → True (decreasing)
      [1, 2, 2, 3] → False (not strict)
      [1, 3, 2]    → False (changes direction)
    """
    if len(route) < 2:
        return True
    # check strictly increasing
    inc = all(route[i] < route[i+1] for i in range(len(route)-1))
    # check strictly decreasing
    dec = all(route[i] > route[i+1] for i in range(len(route)-1))
    return inc or dec

def reposition_diagram (points, in_out_path, paths, typeofproc, print_=False, spacing_=1.0):
    """
    Tries to avoid superposition using a different strategy depending on the type of interaction, e.g.
    - for [2, 2] interactions, it will try to find the 2 longest paths that connect each in-particle with each out-particle, 
    straightening both paths and keeping them at different height, while all the rest of paths connecting them will be inbetween.
    - for [2, 1] interactions, it will try to find which of the 2 particle from one side have the longest path to the other particle,
    making that one straight and at a certain height, making all other points out of said height.
    -etc.
    """
    minx_point = np.min(points[:, 0])
    maxx_point = np.max(points[:, 0])

    for i in range(len(in_out_path)):
        for j in range(len(in_out_path[i, 0])):
            if in_out_path[i, 0][j] == 0:
                continue
            if points[in_out_path[i, 0][j]-1, 0] == maxx_point:
                continue
            else:
                points[in_out_path[i, 0][j]-1, 1] = maxx_point - points[in_out_path[i, 0][j]-1, 0]
                points[in_out_path[i, 0][j]-1, 0] = maxx_point
        for j in range(len(in_out_path[i, 1])):
            if in_out_path[i, 1][j] == 0:
                continue
            if points[in_out_path[i, 1][j]-1, 0] == minx_point:
                continue
            else:
                points[in_out_path[i, 1][j]-1, 1] = - minx_point + points[in_out_path[i, 1][j]-1, 0]
                points[in_out_path[i, 1][j]-1, 0] = minx_point

    if typeofproc == [2, 2]:
        maxy_point = 5
        path1 = find_shortest_undirected_path(paths, in_out_path[0, 0][0], in_out_path[0, 1][0])
        path2 = find_shortest_undirected_path(paths, in_out_path[0, 0][1], in_out_path[0, 1][1])
        path3 = find_shortest_undirected_path(paths, in_out_path[0, 0][0], in_out_path[0, 1][1])
        path4 = find_shortest_undirected_path(paths, in_out_path[0, 0][1], in_out_path[0, 1][0])
        if path1[0] < path3[0]:
            if(print_):
                print(path2[1])
            for i in path1[1]:
                points[i-1, 1] = maxy_point
            if is_ordered_route(path1[1]) == False:
                for i in range(1, len(path1[1])-1):
                    points[path1[1][i]-1, 1] = (maxy_point-1)/2
            for i in path2[1]:
                points[i-1, 1] = 1
            for i in find_same_height_outside (points, path2[1]):
                points[i-1, 1] = (maxy_point-1)/2
        
        else:
            if(print_):
                print(path4[1])
            for i in path3[1]:
                points[i-1, 1] = maxy_point
            if is_ordered_route(path3[1]) == False:
                for i in range(1, len(path3[1])-1):
                    points[path3[1][i]-1, 1] = (maxy_point-1)/2
            for i in path4[1]:
                points[i-1, 1] = 1
            for i in find_same_height_outside (points, path4[1]):
                points[i-1, 1] = (maxy_point-1)/2
    elif typeofproc == [2, 1]:
        maxy_point = 5
        path1 = find_shortest_undirected_path(paths, in_out_path[0, 0][0], in_out_path[0, 1][0])
        path2 = find_shortest_undirected_path(paths, in_out_path[0, 0][0], in_out_path[0, 1][1])
        if path1[0] < path2[0]:
            for i in path1[1]:
                points[i-1, 1] = maxy_point
            if is_ordered_route(path1[1]) == False:
                for i in range(1, len(path1[1])-1):
                    points[path1[1][i]-1, 1] = (maxy_point-1)/2
            for i in path2[1]:
                points[i-1, 1] = 1
            for i in find_same_height_outside (points, path2[1]):
                points[i-1, 1] = (maxy_point-1)/2
        else:
            for i in path2[1]:
                points[i-1, 1] = maxy_point
            if is_ordered_route(path2[1]) == False:
                for i in range(1, len(path2[1])-1):
                    points[path2[1][i]-1, 1] = (maxy_point-1)/2
            for i in path1[1]:
                points[i-1, 1] = 1
            for i in find_same_height_outside (points, path1[1]):
                points[i-1, 1] = (maxy_point-1)/2
    elif typeofproc == [1, 2]:
        maxy_point = 3
        path1 = find_shortest_undirected_path(paths, in_out_path[0, 0][0], in_out_path[0, 1][0])
        path2 = find_shortest_undirected_path(paths, in_out_path[0, 0][1], in_out_path[0, 1][0])
        if path1[0] < path2[0]:
            for i in path1[1]:
                points[i-1, 1] = maxy_point
            if is_ordered_route(path1[1]) == False:
                for i in range(1, len(path1[1])-1):
                    points[path1[1][i]-1, 1] = (maxy_point-1)/2
            for i in path2[1]:
                points[i-1, 1] = 1
            for i in find_same_height_outside (points, path2[1]):
                points[i-1, 1] = (maxy_point-1)/2
        else:
            for i in path2[1]:
                points[i-1, 1] = maxy_point
            if is_ordered_route(path2[1]) == False:
                for i in range(1, len(path2[1])-1):
                    points[path2[1][i]-1, 1] = (maxy_point-1)/2
            for i in path1[1]:
                points[i-1, 1] = 1
            for i in find_same_height_outside (points, path1[1]):
                points[i-1, 1] = (maxy_point-1)/2
    elif typeofproc == [1, 1]:
        maxy_point = 3
        path1 = find_shortest_undirected_path(paths, in_out_path[0, 0][0], in_out_path[0, 1][0])
        if path1[0] < 2:
            for i in path1[1]:
                points[i-1, 1] = maxy_point
            if is_ordered_route(path1[1]) == False:
                for i in range(1, len(path1[1])-1):
                    points[path1[1][i]-1, 1] = maxy_point
        else:
            for i in path1[1]:
                points[i-1, 1] = 1
            for i in find_same_height_outside (points, path1[1]):
                points[i-1, 1] = maxy_point
        
    points = equalize_x_spacing(points, spacing=spacing_)

    return points