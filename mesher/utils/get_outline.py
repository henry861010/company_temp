import numpy as np

def get_outline(elements: np.ndarray, nodes: np.ndarray, return_xy: bool = False):
    """
    Find ordered boundary loops (outlines) for a 2D quad mesh.
    Works with multiple disconnected blocks.

    Parameters
    ----------
    elements : (E, 4) int array
        Node indices (0-based or 1-based both fine; see note below).
    nodes : (N, 3) float array
        Node coordinates [x,y,z]; only x,y are used.
    return_xy : bool
        If True, returns loops as list of (x,y) arrays.
        If False, returns loops as list of node-index arrays.

    Returns
    -------
    loops : list of 1D arrays
        Each entry is an ordered closed loop (first node repeated at the end).
        Type is np.ndarray of ints (node ids) if return_xy=False,
        or np.ndarray of shape (k+1, 2) (x,y) if return_xy=True.
    """

    if elements.size == 0:
        return []

    # If elements are 1-based, normalize to 0-based (detect quickly).
    if elements.min() == 1 and elements.max() <= nodes.shape[0]:
        elems = elements - 1
    else:
        elems = elements

    # Build all edges (undirected) for quads: (n0-n1, n1-n2, n2-n3, n3-n0)
    e0 = elems[:, [0, 1]]
    e1 = elems[:, [1, 2]]
    e2 = elems[:, [2, 3]]
    e3 = elems[:, [3, 0]]
    all_edges = np.vstack([e0, e1, e2, e3])
    all_edges = all_edges[all_edges[:,0] != all_edges[:,1]]

    # Keep a copy with original direction (for possible orientation needs),
    # but use a sorted version to detect duplicates
    undirected = np.sort(all_edges, axis=1)

    # Unique edges and their multiplicity
    # counts==1 => boundary edges; counts==2 => interior edges
    uniq, inv, counts = np.unique(undirected, axis=0, return_inverse=True, return_counts=True)

    boundary_mask = (counts[inv] == 1)
    boundary_edges = all_edges[boundary_mask]                  # use original endpoints

    if boundary_edges.size == 0:
        return []  # no boundary (fully closed surface or empty)

    # Build adjacency on boundary nodes (each boundary edge contributes two directed arcs)
    # For manifold boundaries, each boundary node has degree 2 in this subgraph.
    # We'll walk the adjacency to form ordered loops.
    # Build mapping node -> neighbors using vectorized stacking, then a dict of sets.
    a = boundary_edges[:, 0]
    b = boundary_edges[:, 1]
    # Directed arcs both ways for simple walking
    arcs = np.vstack([np.column_stack([a, b]), np.column_stack([b, a])])  # (2B, 2)

    # Group neighbors per node
    # Sort arcs by source node to allow slicing
    order = np.argsort(arcs[:, 0], kind='mergesort')
    arcs = arcs[order]
    src = arcs[:, 0]
    dst = arcs[:, 1]

    # Indices where src changes
    starts = np.flatnonzero(np.r_[True, src[1:] != src[:-1]])
    # Build a compact neighbor list dict: node -> np.ndarray of neighbors
    neighbor = {}
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(src)
        neighbor[src[s]] = dst[s:e]

    # For fast "edge visited" checks, store edges as sorted tuples
    def edge_key(u, v):
        return (u, v) if u < v else (v, u)

    unvisited = {edge_key(u, v) for (u, v) in boundary_edges}

    loops = []
    while unvisited:
        # Start from an arbitrary unvisited edge
        u, v = next(iter(unvisited))

        # We don't know the orientation; try both directions to walk a closed loop
        start = u
        curr = v
        prev = u
        loop = [start, curr]
        unvisited.discard(edge_key(prev, curr))

        while True:
            nbrs = neighbor.get(curr, np.array([], dtype=elems.dtype))
            # Choose next neighbor that continues the boundary and isn't prev
            nxt_candidates = nbrs[nbrs != prev]

            nxt = None
            for c in nxt_candidates:
                if edge_key(curr, c) in unvisited:
                    nxt = c
                    break

            if nxt is None:
                # Either we've closed (next is start) or hit a non-manifold endpoint.
                # If closed, ensure loop closes; otherwise stop (open boundary).
                if start in nbrs and edge_key(curr, start) in unvisited:
                    # close explicitly
                    unvisited.discard(edge_key(curr, start))
                    loop.append(start)
                break

            loop.append(nxt)
            unvisited.discard(edge_key(curr, nxt))
            prev, curr = curr, nxt

            if curr == start:
                loop.append(start)
                break

        # Ensure it's a proper closed loop with length >= 4 nodes
        if len(loop) >= 4 and loop[0] == loop[-1]:
            loops.append(np.array(loop, dtype=elems.dtype))

    # Optional: make loops counter-clockwise (positive signed area)
    # using x,y only; skip trivial loops.
    xy = nodes[:, :2]
    def signed_area(ids):
        pts = xy[ids]
        x = pts[:, 0]; y = pts[:, 1]
        return 0.5 * np.sum(x[:-1]*y[1:] - x[1:]*y[:-1])

    oriented = []
    for ids in loops:
        if len(ids) < 4:
            continue
        if signed_area(ids) < 0:        # clockwise => reverse
            ids = ids[::-1]
        oriented.append(ids)

    if return_xy:
        return [xy[ids] for ids in oriented]
    else:
        # Return node indices in original indexing if caller used 1-based
        if elements.min() == 1 and elements.max() <= nodes.shape[0]:
            return [ids + 1 for ids in oriented]
        return oriented
