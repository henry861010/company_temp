import numpy as np

def _circle_distance(center_x, center_y, R, nodes, eps=1e-15):
    nodes = np.asarray(nodes, dtype=float)
    c = np.array([center_x, center_y], dtype=float)
    v = nodes - c
    r = np.linalg.norm(v, axis=1)
    d_signed = r - R
    d_abs = np.abs(d_signed)
    inv_r = 1.0 / np.maximum(r, eps)
    unit_normal = (v.T * inv_r).T
    close_node = c + unit_normal * R
    return d_abs, d_signed, close_node, unit_normal

def _segment_circle_intersections(c, r, p1, p2, eps=1e-12):
    p1 = np.asarray(p1, float); p2 = np.asarray(p2, float); c = np.asarray(c, float)
    d = p2 - p1
    f = p1 - c
    a = np.dot(d, d)
    if a < eps: return []
    b = 2.0 * np.dot(d, f)
    cc = np.dot(f, f) - r*r
    disc = b*b - 4*a*cc
    out = []
    if disc < -eps:
        return out
    elif abs(disc) <= eps:
        t = -b / (2*a)
        if -eps <= t <= 1+eps:
            out.append(p1 + t*d)
    else:
        sd = np.sqrt(disc)
        t1 = (-b - sd) / (2*a)
        t2 = (-b + sd) / (2*a)
        if -eps <= t1 <= 1+eps: out.append(p1 + t1*d)
        if -eps <= t2 <= 1+eps: out.append(p1 + t2*d)
    return out

def _inside_or_on_circle(pt, c, r, eps=1e-12):
    return np.dot(pt - c, pt - c) <= r*r + eps

def _unique_points(points, eps=1e-9):
    uniq = []
    for p in points:
        if not any(np.linalg.norm(p - q) <= eps for q in uniq):
            uniq.append(p)
    return uniq

def _star_and_other_inners(center_x, center_y, r, quad_xy, eps=1e-12):
    quad = np.asarray(quad_xy, float).reshape(4, 2)
    c = np.array([center_x, center_y], float)

    # star: nearest vertex to center
    dists = np.linalg.norm(quad - c, axis=1)
    star_idx = int(np.argmin(dists))
    star_node = quad[star_idx]

    # candidates: vertices inside/on circle + segment/circle intersections
    cand = []
    for i in range(4):
        if _inside_or_on_circle(quad[i], c, r, eps):
            cand.append(quad[i])
    for i in range(4):
        j = (i + 1) % 4
        cand.extend(_segment_circle_intersections(c, r, quad[i], quad[j], eps=eps))

    cand = _unique_points([np.asarray(p, float) for p in cand], eps=max(1e-9, 10*eps))
    # drop the star if it’s in candidates
    other = [p for p in cand if np.linalg.norm(p - star_node) > max(1e-9, 10*eps)]

    # clockwise sort about center
    def angle(p):
        v = p - c
        return np.arctan2(v[1], v[0])
    other_sorted = sorted(other, key=angle, reverse=True)
    return star_node, other_sorted

def _checkerboard_center_cylinder(element_size, dim, x_list, y_list, tol=1e-9):
    """
    Keeps quads fully inside the circle. For quads that intersect the circle,
    snaps near-circle boundary nodes to the circle and fills the circular boundary
    with triangles formed as a fan from the star node to clockwise 'other_inners'.
    """
    nodes, elements = _checkerboard_box(element_size, x_list, y_list)  # expect nodes: (N,2), elements: (M,4) ints

    nodes = np.asarray(nodes, float)
    elements = np.asarray(elements, dtype=np.int64)

    center_x, center_y, r = dim
    c = np.array([center_x, center_y], float)
    R2 = (r + tol) ** 2

    # --- classify elements vs circle ---
    elem_xy = nodes[elements]                   # (M,4,2)
    dx = elem_xy[..., 0] - center_x
    dy = elem_xy[..., 1] - center_y
    D2 = dx*dx + dy*dy                          # (M,4)

    inside4 = (D2 <= R2)
    inner_mask = inside4.all(axis=1)            # all 4 inside
    inside_any = inside4.any(axis=1)            # any inside
    boundary_mask = inside_any & (~inner_mask)  # intersects circle
    boundary_elements = elements[boundary_mask] # (Kb,4)
    inner_elements = elements[inner_mask]       # (Ki,4)

    # --- snap near-circle boundary nodes to the circle (threshold tied to element size) ---
    b_nodes = np.unique(boundary_elements.ravel())
    dist_abs, _, close_pts, _ = _circle_distance(center_x, center_y, r, nodes[b_nodes])
    snap_thresh = 0.05 * element_size
    snap_mask = dist_abs < snap_thresh
    nodes[b_nodes[snap_mask]] = close_pts[snap_mask]

    # --- build new nodes/elements for boundary triangles (keep a tolerance-based cache) ---
    new_points = []     # list of points to append after originals
    tri_elems = []      # list of triangle [i0, i1, i2] using global indices (will remap later)

    # quantized key for reuse within tolerance (so neighbors share intersection points)
    q = max(tol, 1e-9)
    qinv = 1.0 / q
    point_index = {}

    def get_or_add_index(pt):
        key = (int(round(pt[0]*qinv)), int(round(pt[1]*qinv)))
        if key in point_index:
            return point_index[key]
        idx = nodes.shape[0] + len(new_points)
        new_points.append(np.asarray(pt, float))
        point_index[key] = idx
        return idx

    # fan triangulation per boundary quad
    for elem in boundary_elements:
        quad_xy = nodes[elem]                     # (4,2)
        star, others = _star_and_other_inners(center_x, center_y, r, quad_xy)

        if len(others) < 2:
            # not enough points to form area (tangent or tiny sliver) -> skip
            continue

        i_star = get_or_add_index(star)
        i0 = get_or_add_index(others[0])
        for p in others[1:]:
            i1 = get_or_add_index(p)
            tri_elems.append([i_star, i0, i1])
            i0 = i1

    # --- assemble final node array ---
    if new_points:
        nodes = np.vstack([nodes, np.vstack(new_points)])

    # --- combine inner quads and boundary triangles, then remap to compact indices ---
    # prepare list-of-arrays with mixed arity; we will keep them separate:
    quad_elems = inner_elements.copy()
    tri_elems = np.asarray(tri_elems, dtype=np.int64)

    # figure used nodes
    used = set()
    if quad_elems.size:
        used.update(int(i) for i in np.unique(quad_elems))
    if tri_elems.size:
        used.update(int(i) for i in np.unique(tri_elems))
    used = np.array(sorted(used), dtype=np.int64)

    mapping = -np.ones(nodes.shape[0], dtype=np.int64)
    mapping[used] = np.arange(used.size, dtype=np.int64)

    nodes = nodes[used]
    if quad_elems.size:
        quad_elems = mapping[quad_elems]
    if tri_elems.size:
        tri_elems = mapping[tri_elems]

    return nodes, quad_elems, tri_elems
