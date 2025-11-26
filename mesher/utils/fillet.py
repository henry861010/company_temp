import numpy as np

def compute_z_max_for_nodes(nodes_xy, inner_box, outer_box, h1, h2):
    """
    nodes_xy: (m, 2) -> (x, y)
    inner_box: (xi_min, yi_min, xi_max, yi_max)
    outer_box: (xo_min, yo_min, xo_max, yo_max)

    Returns:
        z_max: (m,) max allowed height at each (x, y)
    """
    xi_min, yi_min, xi_max, yi_max = inner_box
    xo_min, yo_min, xo_max, yo_max = outer_box

    x = nodes_xy[:, 0]
    y = nodes_xy[:, 1]

    # Center and half sizes of inner/outer boxes
    cx = 0.5 * (xo_min + xo_max)
    cy = 0.5 * (yo_min + yo_max)

    inner_hx = 0.5 * (xi_max - xi_min)
    inner_hy = 0.5 * (yi_max - yi_min)
    outer_hx = 0.5 * (xo_max - xo_min)
    outer_hy = 0.5 * (yo_max - yo_min)

    # Distance from center, normalized from inner box to outer box
    # (0 inside inner box; 1 at outer boundary; >1 outside outer box)
    dx = np.abs(x - cx)
    dy = np.abs(y - cy)

    # Avoid division by zero if inner and outer are same (then no slope)
    eps = 1e-12
    tx = (dx - inner_hx) / np.maximum(outer_hx - inner_hx, eps)
    ty = (dy - inner_hy) / np.maximum(outer_hy - inner_hy, eps)

    # t=0 in inner box, t=1 at outer boundary
    t = np.maximum(tx, ty)
    t = np.clip(t, 0.0, 1.0)

    # Linear interpolation of height from h1 -> h2
    z_max = h1 + t * (h2 - h1)
    return z_max


def filter_elements_in_inclined_box(nodes, elements,
                                    inner_box, outer_box,
                                    h1, h2,
                                    z_min=0.0,
                                    require_all_nodes_inside=True):
    """
    nodes: (m, 3) float, [x, y, z]
    elements: (n, 8) int, node indices for each hex element
    inner_box / outer_box: as above
    h1, h2: top heights at inner + outer
    z_min: bottom plane (default 0.0)
    require_all_nodes_inside:
        True  -> keep element only if all 8 nodes are inside region
        False -> keep element if at least 1 node is inside

    Returns:
        elements_mask: (n,) bool, True means element kept
        filtered_elements: elements[elements_mask]
    """
    nodes = np.asarray(nodes, dtype=float)
    elements = np.asarray(elements, dtype=int)

    x = nodes[:, 0]
    y = nodes[:, 1]
    z = nodes[:, 2]

    xi_min, yi_min, xi_max, yi_max = inner_box
    xo_min, yo_min, xo_max, yo_max = outer_box

    # 1) inside outer XY box
    inside_outer_xy = (
        (x >= xo_min) & (x <= xo_max) &
        (y >= yo_min) & (y <= yo_max)
    )

    # 2) allowed max height at each (x, y)
    z_max = compute_z_max_for_nodes(nodes[:, :2], inner_box, outer_box, h1, h2)

    # 3) within vertical range
    inside_z = (z >= z_min) & (z <= z_max)

    # node_inside: full 3D region
    node_inside = inside_outer_xy & inside_z

    # Map to elements: (n, 8) bool
    elem_node_inside = node_inside[elements]

    if require_all_nodes_inside:
        elements_mask = elem_node_inside.all(axis=1)
    else:
        elements_mask = elem_node_inside.any(axis=1)

    filtered_elements = elements[elements_mask]
    return elements_mask, filtered_elements

import numpy as np

def _max_z(coord, b1, b2, h1, h2, eps=1e-12):
    """
    coord : 1D array of x or y coordinate of candidate nodes
    b1, b2 : inner and outer boundary coordinate along that axis
    h1, h2 : z at inner and outer boundary
    """
    denom = np.maximum(b2 - b1, eps)
    r = (coord - b1) / denom       # 0 at inner, 1 at outer
    max_z = r * (h2 - h1) + h1
    return max_z


def set_fillet(elements, nodes, polygon1, polygon2, z1, z3,
               require_all_nodes_inside=True):
    """
    elements: (Ne,8) int array of node indices
    nodes   : (N,3) float array of node coordinates
    polygon1, polygon2: list/array of (x,y) with same length (inner & outer)
    z1, z3  : lower / upper z of the fillet volume
    """
    x = nodes[:, 0]
    y = nodes[:, 1]
    z = nodes[:, 2]

    N = len(nodes)
    nodes_inside = np.zeros(N, dtype=bool)

    n_edge = len(polygon1)
    for i in range(n_edge):
        node1_pre = polygon1[i - 1]
        node1_post = polygon1[i]
        node2_pre = polygon2[i - 1]
        node2_post = polygon2[i]

        # Bounding box in XY
        x1 = min(node1_pre[0], node1_post[0], node2_pre[0], node2_post[0])
        y1 = min(node1_pre[1], node1_post[1], node2_pre[1], node2_post[1])
        x3 = max(node1_pre[0], node1_post[0], node2_pre[0], node2_post[0])
        y3 = max(node1_pre[1], node1_post[1], node2_pre[1], node2_post[1])

        # Base z filter + XY box filter (IMPORTANT: parentheses for &)
        candidates = (
            (x1 < x) & (x < x3) &
            (y1 < y) & (y < y3) &
            (z1 < z) & (z < z3)
        )

        if not np.any(candidates):
            continue

        # Decide if this edge is roughly vertical or horizontal
        dx = abs(node1_pre[0] - node1_post[0])
        dy = abs(node1_pre[1] - node1_post[1])

        if dx < dy:
            # Edge is more vertical -> inner/outer differ in x => use x-axis
            axis_coord = x[candidates]
            b1 = node1_pre[0]    # inner x
            b2 = node2_pre[0]    # outer x
        else:
            # Edge is more horizontal -> inner/outer differ in y => use y-axis
            axis_coord = y[candidates]
            b1 = node1_pre[1]    # inner y
            b2 = node2_pre[1]    # outer y

        # z-limiter surface for these candidate nodes
        max_z = _max_z(axis_coord, b1, b2, z1, z3)

        # Keep only nodes below the inclined plane
        sub_nodes_z = z[candidates]
        mask_below = sub_nodes_z < max_z

        # Update global node mask (union over all edges)
        idx = np.nonzero(candidates)[0]
        nodes_inside[idx[mask_below]] = True

    # Convert node mask -> element mask
    # candidates_per_element: (Ne,8) bool
    candidates_per_element = nodes_inside[elements]

    if require_all_nodes_inside:
        elements_mask = candidates_per_element.all(axis=1)
    else:
        elements_mask = candidates_per_element.any(axis=1)

    return elements_mask, nodes_inside
