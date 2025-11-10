from __future__ import annotations
import numpy as np
from typing import Iterable, List, Tuple, Dict, Union, Optional

# ---------- slant helpers (subset in any order) ----------

def _slant_vertical(nodes: np.ndarray, indices: np.ndarray, x_from: float, x_to: float) -> np.ndarray:
    nodes = np.asarray(nodes, dtype=float)
    indices = np.asarray(indices, dtype=int)
    target = nodes[indices]
    order = np.argsort(target[:, 1])  # by y
    new_x = np.full(len(indices), x_from) if x_from == x_to else np.linspace(x_from, x_to, len(indices))
    out = nodes.copy()
    out[indices[order], 0] = new_x
    return out

def _slant_horizontal(nodes: np.ndarray, indices: np.ndarray, y_from: float, y_to: float) -> np.ndarray:
    nodes = np.asarray(nodes, dtype=float)
    indices = np.asarray(indices, dtype=int)
    target = nodes[indices]
    order = np.argsort(target[:, 0])  # by x
    new_y = np.full(len(indices), y_from) if y_from == y_to else np.linspace(y_from, y_to, len(indices))
    out = nodes.copy()
    out[indices[order], 1] = new_y
    return out


# ---------- geometry primitives ----------

def _angle_between_dirs_deg(v1: np.ndarray, v2: np.ndarray, eps: float = 1e-15) -> float:
    v1 = np.asarray(v1, float)[:2]
    v2 = np.asarray(v2, float)[:2]
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 < eps or n2 < eps:
        return np.inf
    u1, u2 = v1 / n1, v2 / n2
    c = float(np.clip(abs(np.dot(u1, u2)), -1.0, 1.0))
    return float(np.degrees(np.arccos(c)))

def _perp_distance_point_to_line(p: np.ndarray, p0: np.ndarray, v: np.ndarray, eps: float = 1e-15) -> float:
    v = np.asarray(v, float)[:2]
    if np.linalg.norm(v) < eps:
        return np.inf
    w = np.asarray(p, float)[:2] - np.asarray(p0, float)[:2]
    cross_mag = v[0]*w[1] - v[1]*w[0]
    return abs(cross_mag) / max(np.linalg.norm(v), eps)

def _is_dependent(line1: Tuple[np.ndarray, np.ndarray],
                  line2: Tuple[np.ndarray, np.ndarray],
                  criteria_dis: float,
                  criteria_angle: float) -> Tuple[bool, float, float]:
    p1 = np.asarray(line1[0], float)[:2]
    p2 = np.asarray(line1[1], float)[:2]
    p3 = np.asarray(line2[0], float)[:2]
    p4 = np.asarray(line2[1], float)[:2]
    v1 = p2 - p1
    v2 = p4 - p3
    angle_deg = _angle_between_dirs_deg(v1, v2)
    dist = _perp_distance_point_to_line(p3, p1, v1)
    return (angle_deg <= criteria_angle) and (dist <= criteria_dis), angle_deg, dist


# ---------- clustering of parallel lines into dependent bands ----------

def _line_primary_coord(line: Tuple[np.ndarray, np.ndarray], is_vertical: bool) -> float:
    a = np.asarray(line[0], float)[:2]
    b = np.asarray(line[1], float)[:2]
    return float(0.5 * ((a[0] + b[0]) if is_vertical else (a[1] + b[1])))

def _line_dir(line: Tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    a = np.asarray(line[0], float)[:2]
    b = np.asarray(line[1], float)[:2]
    return b - a

def cluster_parallel_lines(
    pattern_list: Iterable[Tuple[np.ndarray, np.ndarray]],
    is_vertical: bool,
    criteria_dis: float,
    criteria_angle: float,
    angle_eps: float = 1e-7,
) -> List[List[Tuple[np.ndarray, np.ndarray]]]:
    """
    Returns a list of clusters; each cluster is a list of lines in increasing primary coord.
    """
    lines = list(pattern_list)
    if not lines:
        return []

    prim = np.array([_line_primary_coord(L, is_vertical) for L in lines])
    dirs = np.array([_line_dir(L) for L in lines])
    order = np.argsort(prim)
    sorted_lines = [lines[i] for i in order]
    sorted_dirs  = dirs[order]

    clusters: List[List[Tuple[np.ndarray, np.ndarray]]] = []
    current_cluster = [sorted_lines[0]]
    ref_dir = sorted_dirs[0]

    for i in range(1, len(sorted_lines)):
        L = sorted_lines[i]
        v = sorted_dirs[i]
        ang = _angle_between_dirs_deg(ref_dir, v)

        if ang <= max(criteria_angle, angle_eps):
            # check dependency against ANY line in the current cluster
            dep_any = any(_is_dependent(last, L, criteria_dis, criteria_angle)[0]
                        for last in current_cluster)
            if dep_any:
                current_cluster.append(L)
                ref_dir = v               # optional: or keep original ref_dir
                continue                  # go to next i

        # not dependent (angle too large or distance too big): start new cluster
        clusters.append(current_cluster)
        current_cluster = [L]
        ref_dir = v

    clusters.append(current_cluster)
    return clusters
