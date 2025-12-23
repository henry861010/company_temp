import numpy as np

EPS = 1e-8

def ray_plane_intersect(ray_o, ray_d, p0, n):
    denom = np.dot(ray_d, n)
    if abs(denom) < EPS:
        return None  # parallel

    t = np.dot(p0 - ray_o, n) / denom
    if t <= EPS:
        return None  # behind or too close

    return ray_o + t * ray_d

def point_in_polygon_3d(pt, poly, n):
    # Project to dominant axis
    ax = np.argmax(np.abs(n))
    idx = [0, 1, 2]
    idx.pop(ax)

    p = poly[:, idx]
    x, y = pt[idx]

    inside = False
    j = len(p) - 1
    for i in range(len(p)):
        xi, yi = p[i]
        xj, yj = p[j]
        if ((yi > y) != (yj > y)) and \
           (x < (xj - xi) * (y - yi) / (yj - yi + EPS) + xi):
            inside = not inside
        j = i
    return inside

def inward_normal_brep(face, faces):
    """
    face: dict with keys:
        - 'point': (3,)
        - 'normal': (3,)
        - 'polygon': (N,3)
    faces: list of all faces (including itself)
    """
    p0 = face['point']
    n = face['normal'] / np.linalg.norm(face['normal'])

    ray_o = p0 + EPS * n
    ray_d = n

    hits = 0
    for f in faces:
        if f is face:
            continue

        hit = ray_plane_intersect(ray_o, ray_d, f['point'], f['normal'])
        if hit is None:
            continue

        if point_in_polygon_3d(hit, f['polygon'], f['normal']):
            hits += 1

    if hits % 2 == 0:
        n = -n

    return n
