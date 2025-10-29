import numpy as np

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

def _checkerboard_cylinder(element_size, dim, x_list, y_list, eps=1e-9):
    def _snap_boundary_nodes_to_circle(nodes, boundary_elements, center_x, center_y, R, element_size, eps=1e-12):
        """
        Snap boundary nodes that are near the circle to the circle.

        nodes:             (N,2) float array; will be modified in place and also returned
        boundary_elements: (E,k) int array of node indices
        center_x, center_y, R: circle parameters
        element_size:      characteristic element size; we snap if distance-to-circle < 0.05 * element_size
        eps:               numerical tolerance
        only_inside:       if True, only consider boundary nodes strictly inside the circle; otherwise consider all boundary nodes
        """
        nodes = np.asarray(nodes, dtype=float)
        b_nodes = np.unique(np.asarray(boundary_elements, dtype=np.int64).ravel())
        if b_nodes.size == 0:
            return nodes

        c = np.array([center_x, center_y, 0], dtype=float)
        r = float(R)
        r2 = r*r

        # Boundary node positions
        P = nodes[b_nodes]                           # (Kb, 2)
        d2 = np.sum((P - c)**2, axis=1)              # squared distance to center

        # --- Prefilter by a squared-distance band to avoid sqrt for far nodes ---
        # If |d - r| < snap_thresh  =>  |d^2 - r^2| < (d + r)*snap_thresh ≈ (2r)*snap_thresh for near-circle d≈r
        snap_thresh = 0.05 * element_size
        band = 2.0 * r * snap_thresh + snap_thresh**2  # a safe over-approx
        near_mask = np.abs(d2 - r2) <= band

        if not np.any(near_mask):
            return nodes

        # Refine only the near candidates using exact distance
        idx = b_nodes[near_mask]
        Pn  = P[near_mask]                            # (K,2)
        d   = np.sqrt(np.maximum(d2[near_mask], eps)) # distance to center (avoid sqrt(0))
        dist_abs = np.abs(d - r)                      # distance to the circle along radius

        # Final snap mask with true absolute distance
        snap_mask = dist_abs < snap_thresh
        if not np.any(snap_mask):
            return nodes

        idx = idx[snap_mask]
        Pn  = Pn[snap_mask]
        d   = d[snap_mask][:, None]                   # (K,1) for broadcasting

        # Unit normals from center to node; safe divide (d already >= eps)
        unit = (Pn - c) / d                           # (K,2)

        # New positions exactly on the circle
        nodes[idx] = c + unit * r

        return nodes

    def _segment_circle_intersections(c, r, p1, p2, eps=1e-12):
        """
        Return intersection points between segment p1->p2 and circle (c, r).
        Each returned point lies on the segment (0<=t<=1). Dedup handled by caller.
        """
        p1 = np.asarray(p1, dtype=np.float32)
        p2 = np.asarray(p2, dtype=np.float32)
        c = np.asarray(c, dtype=np.float32)
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

    def _is_on_circle(pt, c, r, eps=1e-12):
        pt = np.asarray(pt, dtype=np.float32)
        d = np.linalg.norm(pt - c)
        return abs(d - r) <= eps
    
    def _is_inside_circle(pt, c, r, eps=1e-12):
        pt = np.asarray(pt, float)
        d2 = np.dot(pt - c, pt - c)
        return d2 < (r - eps) ** 2
    
    def _is_inside_or_on_circle(pt, c, r, eps=1e-12):
        pt = np.asarray(pt, dtype=np.float32)
        return np.dot(pt - c, pt - c) <= r*r + eps

    def _star_and_other_inners(center_n, r, quad_xy, eps=1e-12):
        """
        quad_xy: shape (4,3) array-like, vertices in polygon order.
        Returns:
            star_idx: int in [0..3]
            star_node: (2,) np.array
            other_inners: list of (2,) np.array points inside/on circle or intersections,
                        excluding star_node, sorted clockwise about center.
        """
        def _is_near_to_existed_node(node, candidates, eps=0.1):
            node = np.asarray(node, float)
            C = np.asarray(candidates, float)
            if C.size == 0:
                return False
            # squared distances (avoid sqrt)
            d2 = np.sum((C - node)**2, axis=1)
            return np.any(d2 <= eps*eps)
    
        def _unique_points(points, eps=1e-9):
            """Deduplicate by Euclidean distance within eps; preserves order."""
            uniq = []
            for p in points:
                if not any(np.linalg.norm(p - q) <= eps for q in uniq):
                    uniq.append(p)
            return np.array(uniq, dtype=np.float32)
        
        def _circular_clockwise_min_gap(points, center):
            """
            points: (N,2)
            center: (2,)
            Returns indices that order points clockwise and start after the largest gap.
            """
            P = np.asarray(points, float)
            c = np.asarray(center, float)
            v = P - c
            ang = np.arctan2(v[:,1], v[:,0])         # (-pi, pi]
            order = np.argsort(-ang, kind='stable')  # clockwise (decreasing angle)
            ang_sorted = ang[order]

            # circular gaps (clockwise): angle[i] -> angle[i+1], with wrap from last->first
            # gap_i = (ang_sorted[i] - ang_sorted[i+1]) mod 2π
            diffs = (ang_sorted - np.roll(ang_sorted, -1)) % (2*np.pi)

            # start after the largest gap
            k = int(np.argmax(diffs))
            order_rot = np.roll(order, -(k+1))
            return points[order_rot]
        
        quad = np.asarray(quad_xy, dtype=np.float32).reshape(4, 3)

        # 1) star = nearest vertex to center
        dists = np.linalg.norm(quad - center_n, axis=1)
        star_idx = int(np.argmin(dists))
        star_node = quad[star_idx]
        
        if _is_on_circle(star_node, center_n, r, eps):
            return None, []

        # 2) collect candidate inner points (vertices inside/on circle, NOT including star yet)
        candidates_existed = []
        for i in range(4):
            if i != star_idx and _is_inside_or_on_circle(quad[i], center_n, r, eps):
                candidates_existed.append(quad[i])

        # 3) add circle-segment intersections (on edges)
        candidates_intersect = []
        for i in range(4):
            j = (i + 1) % 4
            inters = _segment_circle_intersections(center_n, r, quad[i], quad[j], eps=eps)

            if len(inters) == 2:
                candidates_intersect.extend([quad[i], quad[j]])
            elif len(inters) == 1:
                if not _is_near_to_existed_node(inters[0], candidates_existed):
                    candidates_intersect.append(inters[0])

        # 6) sort clockwise about center (angle decreasing)
        candidates = candidates_existed + candidates_intersect
        candidates = _unique_points([np.asarray(p, float) for p in candidates], eps=max(1e-9, 10*eps))
        
        other_sorted = _circular_clockwise_min_gap(candidates, center_n)
        
        return star_node, other_sorted

    nodes, elements = _checkerboard_box(element_size, x_list, y_list)

    center_x, center_y, R = dim
    center_n = np.array([center_x, center_y, 0], dtype=np.float32)
    R2 = (R + eps) ** 2

    ### find the inner/boundary elements
    elem_xy = nodes[elements]
    dx = elem_xy[..., 0] - center_x
    dy = elem_xy[..., 1] - center_y
    D2 = dx*dx + dy*dy 

    inside4 = (D2 <= R2)
    inner_mask = inside4.all(axis=1)      # all four inside
    inside_any = inside4.any(axis=1)      # at least one inside
    boundary_mask = inside_any & (~inner_mask)

    ### Only consider nodes that belong to boundary elements
    boundary_elements = elements[boundary_mask]
    
    ### move the node of small one
    nodes = _snap_boundary_nodes_to_circle(nodes, boundary_elements, center_x, center_y, R, element_size, eps)
    
    ### remain the inner part only
    elements = elements[inner_mask]
    used_nodes = np.unique(elements)
    mapping = -np.ones(len(nodes), dtype=np.int32)
    mapping[used_nodes] = np.arange(len(used_nodes))
    elements = mapping[elements]
    nodes_o = nodes
    nodes = nodes[used_nodes]
    #return nodes, elements

    ### mesh
    for element in boundary_elements:
        star_node, other_inners = _star_and_other_inners(center_n, R, nodes_o[element])
        if  star_node is not None and len(other_inners):
            star_node_index = len(nodes)
            nodes = np.vstack([nodes, star_node])
            nodes = np.vstack([nodes, other_inners[0]])
            for i, inner in enumerate(other_inners[1:]):
                nodes = np.vstack([nodes, inner])
                elements = np.vstack([elements, [star_node_index, len(nodes)-2, len(nodes)-1, len(nodes)-1]])
    return nodes, elements