import numpy as np
from matplotlib.path import Path

def mask_quads_fully_inside_polygon(elements_xy8, polygon_xy, include_boundary=True, eps=1e-12):
    quads = np.asarray(elements_xy8, float).reshape(-1, 4, 2)  # (N,4,2)
    poly  = np.asarray(polygon_xy, float)
    path  = Path(poly)

    # --- quick bbox prefilter to cut candidates down ---
    qmin = quads.min(axis=1)    # (N,2)
    qmax = quads.max(axis=1)    # (N,2)
    pmin = poly.min(axis=0)     # (2,)
    pmax = poly.max(axis=0)     # (2,)
    cand = (qmax[:,0] >= pmin[0]) & (qmin[:,0] <= pmax[0]) & \
           (qmax[:,1] >= pmin[1]) & (qmin[:,1] <= pmax[1])

    N = len(quads)
    keep = np.zeros(N, dtype=bool)
    if not np.any(cand):
        return keep

    qc = quads[cand]  # candidates only

    # --- vertices-inside test ---
    # include boundary by using a small negative radius (treat boundary as inside)
    rad = (-eps if include_boundary else 0.0)
    vin = path.contains_points(qc.reshape(-1,2), radius=rad).reshape(-1,4).all(axis=1)

    # --- edge intersection test: no quad edge may cross any polygon edge ---
    # Build quad edges (flattened)
    P = qc[:, [0,1,2,3], :].reshape(-1, 2)   # starts
    Q = qc[:, [1,2,3,0], :].reshape(-1, 2)   # ends
    M = P.shape[0]                           # 4 * (#candidates)

    # polygon edges
    R_all = poly
    S_all = np.roll(poly, -1, axis=0)

    def cross2(a, b):  # 2D cross product z-component
        return a[...,0]*b[...,1] - a[...,1]*b[...,0]

    intersects_any = np.zeros(M, dtype=bool)
    for r, s in zip(R_all, S_all):
        u   = Q - P            # (M,2)
        rs  = s - r            # (2,)
        o1  = cross2(u, r - P) # orient(P,Q,r)
        o2  = cross2(u, s - P) # orient(P,Q,s)
        o3  = cross2(rs, P - r)
        o4  = cross2(rs, Q - r)

        # proper intersection
        proper = (o1*o2 < -eps) & (o3*o4 < -eps)

        # colinear/boundary overlap cases (count as intersection unless include_boundary==True)
        def between(a, b, c):
            mn = np.minimum(a, b) - eps
            mx = np.maximum(a, b) + eps
            return (c[...,0] >= mn[...,0]) & (c[...,0] <= mx[...,0]) & \
                   (c[...,1] >= mn[...,1]) & (c[...,1] <= mx[...,1])

        col1 = (np.abs(o1) <= eps) & between(P, Q, r)
        col2 = (np.abs(o2) <= eps) & between(P, Q, s)
        col3 = (np.abs(o3) <= eps) & between(np.broadcast_to(r, P.shape), np.broadcast_to(s, P.shape), P)
        col4 = (np.abs(o4) <= eps) & between(np.broadcast_to(r, Q.shape), np.broadcast_to(s, Q.shape), Q)

        boundary_touch = col1 | col2 | col3 | col4
        intersects = proper | (boundary_touch & (not include_boundary))
        intersects_any |= intersects

        # small early exit if everything already intersects
        if intersects_any.all():
            break

    # reduce intersections back to per-quad
    touches = intersects_any.reshape(-1, 4).any(axis=1)

    # fully-inside for candidates = (all vertices inside) AND (no edge touches/crosses)
    full_in = vin & ~touches

    keep[cand] = full_in
    return keep
