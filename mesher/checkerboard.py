def _checkerboard_box(element_size, x_list, y_list):
    ### validate element_size
    if not np.isscalar(element_size) or float(element_size) <= 0:
        raise ValueError("element_size must be a positive scalar.")
    h = float(element_size)

    ### normalize inputs
    x_list = np.asarray(x_list, dtype=np.float32).ravel()
    y_list = np.asarray(y_list, dtype=np.float32).ravel()
    if x_list.ndim != 1 or y_list.ndim != 1 or x_list.size < 2 or y_list.size < 2:
        raise ValueError("x_list and y_list must be 1D arrays with length >= 2.")

    ### monotonic check
    if np.any(np.diff(x_list) < 0) or np.any(np.diff(y_list) < 0):
        raise ValueError("x_list and y_list must be non-decreasing.")

    ### densify helper (handles zero-length spans)
    def densify(arr):
        out = []
        for a, b in zip(arr[:-1], arr[1:]):
            length = float(b - a)
            if length == 0.0:
                # duplicate line: keep only one point when joining segments
                if not out:
                    out.append(a)
                continue
            nseg = max(1, int(np.ceil(length / h)))
            seg = np.linspace(a, b, nseg + 1, endpoint=True, dtype=np.float32)
            if out:
                seg = seg[1:]  # avoid boundary duplicate
            out.extend(seg.tolist())
        return np.asarray(out, dtype=np.float32)

    x = densify(x_list)
    y = densify(y_list)
    if x.size < 2 or y.size < 2:
        raise ValueError("After densify, need at least 2 x-lines and 2 y-lines.")

    Nx, Ny = int(x.size), int(y.size)

    ### nodes (x varies fastest)
    X, Y = np.meshgrid(x, y, indexing="xy")
    Z = np.zeros_like(X)
    nodes = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()]).astype(np.float32)  # (Ny*Nx, 2)

    ### element node ids
    ix = np.arange(Nx - 1, dtype=np.int32)
    iy = np.arange(Ny - 1, dtype=np.int32)
    GX, GY = np.meshgrid(ix, iy, indexing="xy")

    n00 = (GY    ) * Nx + (GX    )  # BL
    n10 = (GY    ) * Nx + (GX + 1)  # BR
    n11 = (GY + 1) * Nx + (GX + 1)  # TR
    n01 = (GY + 1) * Nx + (GX    )  # TL

    # CLOCKWISE: BL, TL, TR, BR
    elements = np.stack([n00, n01, n11, n10], axis=-1).reshape(-1, 4).astype(np.int32)
    
    return nodes, elements

def _circle_distance(center_x, center_y, R, nodes, eps=1e-15):
    """
    nodes: (N,2)
    Returns:
      d_abs: (N,)  | ||p-c|| - R |
      d_signed: (N,)  ||p-c|| - R   (neg inside, pos outside)
      close_node: (N,2) closest points on the circle
      unit_normal: (N,2) outward unit normals at close_node
    """
    nodes = np.asarray(nodes, dtype=float)
    c = np.array([center_x, center_y], dtype=float)

    v = nodes - c                # (N,2)
    r = np.linalg.norm(v, axis=1)
    d_signed = r - R
    d_abs = np.abs(d_signed)

    inv_r = 1.0 / np.maximum(r, eps)
    unit_normal = (v.T * inv_r).T    # (N,2)
    close_node = c + unit_normal * R # (N,2)
    return d_abs, d_signed, close_node, unit_normal

def _segment_circle_intersections(c, r, p1, p2, eps=1e-12):
    """
    Return intersection points between segment p1->p2 and circle (c, r).
    Each returned point lies on the segment (0<=t<=1). Dedup handled by caller.
    """
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    c = np.asarray(c, dtype=float)
    d = p2 - p1
    f = p1 - c

    a = np.dot(d, d)
    b = 2.0 * np.dot(d, f)
    cc = np.dot(f, f) - r*r
    if a < eps:
        return []  # degenerate segment

    disc = b*b - 4*a*cc
    out = []
    if disc < -eps:
        return out
    elif abs(disc) <= eps:
        t = -b / (2*a)
        if -eps <= t <= 1+eps:
            out.append(p1 + t*d)
    else:
        sqrt_disc = np.sqrt(disc)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        if -eps <= t1 <= 1+eps:
            out.append(p1 + t1*d)
        if -eps <= t2 <= 1+eps:
            out.append(p1 + t2*d)
    return out

def _inside_or_on_circle(pt, c, r, eps=1e-12):
    return np.dot(pt - c, pt - c) <= r*r + eps

def _unique_points(points, eps=1e-9):
    """Deduplicate by Euclidean distance within eps; preserves order."""
    uniq = []
    for p in points:
        if not any(np.linalg.norm(p - q) <= eps for q in uniq):
            uniq.append(p)
    return uniq

def _star_and_other_inners(center_x, center_y, r, quad_xy, eps=1e-12):
    """
    quad_xy: shape (4,2) array-like, vertices in polygon order.
    Returns:
        star_idx: int in [0..3]
        star_node: (2,) np.array
        other_inners: list of (2,) np.array points inside/on circle or intersections,
                      excluding star_node, sorted clockwise about center.
    """
    quad = np.asarray(quad_xy, dtype=float).reshape(4, 2)
    c = np.array([center_x, center_y], dtype=float)

    # 1) star = nearest vertex to center
    dists = np.linalg.norm(quad - c, axis=1)
    star_idx = int(np.argmin(dists))
    star_node = quad[star_idx]

    # 2) collect candidate inner points (vertices inside/on circle, NOT including star yet)
    candidates = []
    for i in range(4):
        if _inside_or_on_circle(quad[i], c, r, eps):
            candidates.append(quad[i])

    # 3) add circle-segment intersections (on edges)
    for i in range(4):
        j = (i + 1) % 4
        inters = _segment_circle_intersections(c, r, quad[i], quad[j], eps=eps)
        candidates.extend(inters)

    # 4) dedup
    candidates = _unique_points([np.asarray(p, float) for p in candidates], eps=max(1e-9, 10*eps))

    # 5) exclude the star node (by proximity)
    other = [p for p in candidates if np.linalg.norm(p - star_node) > max(1e-9, 10*eps)]

    # 6) sort clockwise about center (angle decreasing)
    def angle(p):
        v = p - c
        return np.arctan2(v[1], v[0])
    other_sorted = sorted(other, key=angle, reverse=True)

    return star_node, other_sorted

def _checkerboard_center_cylinder(element_size, dim, x_list, y_list, tol=1e-9):
    nodes, elements = _checkerboard_box(element_size, x_list, y_list)

    center_x, center_y, r = dim
    R2 = (R + tol) ** 2

    ### find the inner/boundary elements
    elem_xy = nodes[elements]
    dx = elem_xy[..., 0] - center_x
    dy = elem_xy[..., 1] - center_y
    D2 = dx*dx + dy*dy 

    inside4 = (D2 <= R2)
    inner_mask = inside4.all(axis=1)      # all four inside
    inside_any = inside4.any(axis=1)      # at least one inside
    boundary_mask = inside_any & (~inner_mask)
    boundary_elements = elements[boundary_mask]

    ### Only consider nodes that belong to boundary elements
    b_nodes = np.unique(boundary_elements.ravel())   # (Nb,)

    ### Threshold band (tune): e.g., 5% of element size
    snap_thresh = 0.05 * element_size

    dist_abs, _, close_pts, _ = _circle_distance(center_x, center_y, r, nodes[b_nodes])
    snap_mask = dist_abs < snap_thresh
    nodes[b_nodes[snap_mask]] = close_pts[snap_mask]
    
    ### remain the inner part only
    elements = elements[inner_mask]
    used_nodes = np.unique(elements)
    mapping = -np.ones(len(nodes), dtype=np.int32)
    mapping[used_nodes] = np.arange(len(used_nodes))
    elements = mapping[elements]
    nodes = nodes[used_nodes]

    ### mesh
    for element in boundary_elements:
        star_node, other_inners = _star_and_other_inners(center_x, center_y, r, element)
        
        star_node_index = len(nodes)
        nodes.append(star_node)
        nodes.append(other_inners[0])
        for inner in other_inners[1:]:
            nodes.append(inner)
            elements.append([star_node_index, len(nodes)-1, len(nodes)])
            
    return nodes, elements