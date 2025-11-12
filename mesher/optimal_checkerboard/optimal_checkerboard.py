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

def _is_dependent(line1: Tuple[npndarray, np.ndarray],
                  line2: Tuple[np.ndarray, np.ndarray],
                  criteria_dis: float,
                  criteria_angle: float) -> Tuple[bool, float, float]:
    p1 = np.asarray(line1[0], float)[:2]
    p2 = np.asarray(line1[1], float)[:2]
    p3 = np.asarray(line2[0], float)[:2]
    p4 = np.asarray(line2[1], float)[:2]
    s


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
            last = current_cluster[-1]
            dep, _, _ = _is_dependent(last, L, criteria_dis, criteria_angle)
            if dep:
                current_cluster.append(L)
                ref_dir = v
                continue
        clusters.append(current_cluster)
        current_cluster = [L]
        ref_dir = v

    clusters.append(current_cluster)
    return clusters


# ---------- dict view (merged as requested) ----------

def clusters_to_dict(
    clusters: List[List[Tuple[np.ndarray, np.ndarray]]],
    is_vertical: bool,
    key_round: Optional[int] = None
) -> Dict[float, List[Tuple[np.ndarray, np.ndarray]]]:
    """
    Convert clusters into a dict keyed by the first line’s primary coord.
    Optionally round the key to 'key_round' decimals to stabilize float keys.
    """
    out: Dict[float, List[Tuple[np.ndarray, np.ndarray]]] = {}
    for cluster in clusters:
        key = _line_primary_coord(cluster[0], is_vertical)
        if key_round is not None:
            key = round(key, key_round)
        out[key] = cluster
    return out


# ---------- convenience wrapper: clusters OR dict ----------

def cluster_parallel_lines_dict(
    pattern_list: Iterable[Tuple[np.ndarray, np.ndarray]],
    is_vertical: bool,
    criteria_dis: float,
    criteria_angle: float,
    angle_eps: float = 1e-7,
    key_round: Optional[int] = None,
    return_dict: bool = True,
) -> Union[Dict[float, List[Tuple[np.ndarray, np.ndarray]]],
           List[List[Tuple[np.ndarray, np.ndarray]]]]:
    """
    One-call convenience: cluster lines, and (by default) return a dict keyed by
    the first line’s primary coordinate. Set return_dict=False to get the clusters list.
    """
    clusters = cluster_parallel_lines(
        pattern_list, is_vertical, criteria_dis, criteria_angle, angle_eps
    )
    if return_dict:
        return clusters_to_dict(clusters, is_vertical, key_round=key_round)
    return clusters
