import numpy as np

def get_outline(elements: np.ndarray, nodes: np.ndarray):
    """
    elements: (E,4) int, node ids of quads (triangles allowed if last two equal)
    nodes   : (N,3) float, coordinates [x,y,z]

    Returns:
        hull_loops_idx  : List[List[int]] each loop is a list of node indices (CW)
        hole_loops_idx  : List[List[int]] each loop is a list of node indices (CCW)
        hull_loops_xy   : List[np.ndarray] coords (x,y,z) for each hull loop
        hole_loops_xy   : List[np.ndarray] coords (x,y,z) for each hole loop
    """
    if elements.size == 0:
        return [], [], [], []

    # Normalize to 0-based if input is 1-based (quick heuristic).
    if elements.min() >= 1 and elements.max() <= nodes.shape[0]:
        elems = elements - 1
    else:
        elems = elements

    # Build all undirected boundary-candidate edges (ignore degenerate edges)
    e0 = elems[:, [0, 1]]
    e1 = elems[:, [1, 2]]
    e2 = elems[:, [2, 3]]
    e3 = elems[:, [3, 0]]
    all_edges = np.vstack([e0, e1, e2, e3])
    all_edges = all_edges[all_edges[:, 0] != all_edges[:, 1]]

    # Count multiplicity on undirected edges -> boundary = multiplicity == 1
    undirected = np.sort(all_edges, axis=1)
    uniq, inv, counts = np.unique(undirected, axis=0, return_inverse=True, return_counts=True)
    boundary_mask = (counts[inv] == 1)
    boundary_edges = all_edges[boundary_mask]

    if boundary_edges.size == 0:
        return [], [], [], []

    # Adjacency as multi-graph (degree typically 2 on boundaries)
    adj = {}
    for a, b in boundary_edges:
        a, b = int(a), int(b)
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)

    # Walk all edges to extract closed loops; mark edges as visited (undirected)
    def edge_key(u, v):
        return (u, v) if u <= v else (v, u)

    unvisited = set(edge_key(int(a), int(b)) for a, b in boundary_edges)
    loops = []

    while unvisited:
        # Start from any unvisited edge
        u, v = next(iter(unvisited))
        # Choose a starting direction (u -> v)
        start = u
        prev = u
        curr = v
        loop = [start]

        # consume the starting edge
        unvisited.discard(edge_key(prev, curr))

        # walk until we come back to start
        while curr != start:
            loop.append(curr)
            nbrs = adj[curr]
            # choose the neighbor that isn't the previous and that still has an unvisited edge
            nxt = None
            for n in nbrs:
                if n != prev and edge_key(curr, n) in unvisited:
                    nxt = n
                    break
            # If not found above (e.g., we arrived from the only unvisited neighbor), try the other neighbor
            if nxt is None:
                for n in nbrs:
                    if edge_key(curr, n) in unvisited:
                        nxt = n
                        break
            # If still None, we’re at the last edge back to start
            if nxt is None:
                nxt = start

            unvisited.discard(edge_key(curr, nxt))
            prev, curr = curr, nxt

        loops.append(loop)

    # Geometry helpers (use x,y only)
    xy = nodes[:, :2]

    def signed_area(idx_loop):
        # Shoelace; positive => CCW, negative => CW
        pts = xy[idx_loop]
        x = pts[:, 0]
        y = pts[:, 1]
        return 0.5 * np.sum(x * np.roll(y, -1) - y * np.roll(x, -1))

    def point_in_poly(pt, idx_loop):
        # Ray casting, returns True if pt is strictly inside polygon
        x, y = pt
        poly = xy[idx_loop]
        inside = False
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            # Check if edge crosses the horizontal ray
            cond1 = (y1 > y) != (y2 > y)
            if cond1:
                x_int = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                if x_int > x:
                    inside = not inside
        return inside

    # Classify loops by nesting depth:
    # depth = number of other loops that contain this loop's centroid.
    # Even depth => outer boundary (hull). Odd depth => hole.
    centroids = [nodes[loop[0], :2] for loop in loops]
    depths = []
    for i, c in enumerate(centroids):
        depth = 0
        for j, idx_j in enumerate(loops):
            if i == j:
                continue
            if point_in_poly(c, idx_j):
                depth += 1
        depths.append(depth)

    hull_loops_idx, hole_loops_idx = [], []

    # Enforce orientation: hull -> CW (negative area), hole -> CCW (positive area)
    for idx_loop, depth in zip(loops, depths):
        A = signed_area(idx_loop)
        if depth % 2 == 0:
            # hull -> CW
            if A > 0:
                idx_loop = list(reversed(idx_loop))
            hull_loops_idx.append(idx_loop)
        else:
            # hole -> CCW
            if A < 0:
                idx_loop = list(reversed(idx_loop))
            hole_loops_idx.append(idx_loop)

    # Also return coordinates (x,y,z) for convenience
    hull_loops_xyz = [nodes[idx] for idx in hull_loops_idx]
    hole_loops_xyz = [nodes[idx] for idx in hole_loops_idx]

    return hull_loops_idx, hole_loops_idx, hull_loops_xyz, hole_loops_xyz
