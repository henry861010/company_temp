import numpy as np

class Polygon:
    def __init__(self, hull, holes=None):
        self.hull = hull  # List of (x,y,z)
        self.holes = holes or []

def _get_edge_key(p1, p2):
    """Standardizes vertex pairs into a hashable unique key."""
    p1_t, p2_t = tuple(np.round(p1, 6)), tuple(np.round(p2, 6))
    return tuple(sorted((p1_t, p2_t)))
    
def _solve_gf2(matrix_a, vector_b):
    """
    Solves the linear system Ax = b over the Galois Field GF(2).
    
    This is used to find edge segment counts such that the sum of 
    segments around every polygon is even. In GF(2), addition is 
    equivalent to XOR, and subtraction is the same as addition.

    Args:
        matrix_a (np.ndarray): Binary incidence matrix (Planes x Free Edges).
        vector_b (np.ndarray): Binary parity targets for each plane.

    Returns:
        np.ndarray: A binary vector where 1 represents an odd number of 
                    segments and 0 represents an even number.
    """
    # Work on copies to avoid modifying inputs
    A = matrix_a.astype(np.int8).copy()
    b = vector_b.astype(np.int8).copy()
    
    rows, cols = A.shape
    pivot_row = 0
    pivot_cols = []

    # Gaussian Elimination
    for j in range(cols):
        if pivot_row >= rows:
            break
        k = np.argmax(A[pivot_row:, j]) + pivot_row
        if A[k, j] == 0:
            continue

        A[[pivot_row, k]] = A[[k, pivot_row]]
        b[[pivot_row, k]] = b[[k, pivot_row]]

        for i in range(rows):
            if i != pivot_row and A[i, j] == 1:
                A[i] ^= A[pivot_row]
                b[i] ^= b[pivot_row]
        
        pivot_cols.append((pivot_row, j))
        pivot_row += 1

    # Check for consistency: Any row of 0s in A must have 0 in b
    for i in range(pivot_row, rows):
        if b[i] != 0:
            return None # Inconsistent system

    x = np.zeros(cols, dtype=int)
    for r, c in pivot_cols:
        x[c] = b[r]
    return x

def _det_edge_count(polygon_objs, fixed_segments=None):
    """
    Generates a topologically consistent edge-plane structure for 3D objects.

    ALGORITHM BACKGROUND:
    To ensure a face can be quad-meshed, the sum of segments on its boundary 
    must be even. We map this to a system of linear equations over GF(2).
    - If an edge is 'free', we solve for its value (1 or 2).
    - If an edge is 'fixed', it acts as a constant in the equation Ax = b.
    - Since every edge is shared by exactly two planes in a manifold, 
      the system is naturally balanced.

    INPUTS:
    :param polygon_objs: List of objects with .hull and .holes (list of points).
    :param fixed_segments: Dict mapping ((p1), (p2)) to an integer segment count.

    RETURNS:
    A dictionary containing:
    - "edge_coords": List of unique edges as tuples of vertex coordinates.
    - "edge_counts": Array of integers (1 or 2, or fixed value) for 
      each unique edge.
    """
    if fixed_segments is None:
        fixed_segments = {}

    unique_edges = [] # a list of key edge (edge index to edge key)
    edge_to_planes = [] # edge index to plane index
    plane_to_edges = [] # plane index to edge index
    edge_hash = {} # edge key to edge index

    # --- 1. TOPOLOGICAL MAPPING ---
    # Visit every polygon and identify unique edges via hashing.
    for p_idx, poly in enumerate(polygon_objs):
        current_plane_edges = []
        loops = [poly.hull] + poly.holes
        for loop in loops:
            n = len(loop)
            for i in range(n):
                key = _get_edge_key(loop[i], loop[(i + 1) % n])
                if key not in edge_hash:
                    edge_hash[key] = len(unique_edges)
                    unique_edges.append(key)
                    edge_to_planes.append([])

                e_idx = edge_hash[key]
                edge_to_planes[e_idx].append(p_idx)
                current_plane_edges.append(e_idx)
        plane_to_edges.append(current_plane_edges)

    # --- 2. SYSTEM ASSEMBLY (Ax = b) ---
    # Map predefined segments to indices and identify free variables.
    fixed_indices = {}
    for edge_pts, count in fixed_segments.items():
        key = _get_edge_key(edge_pts[0], edge_pts[1])
        if key in edge_hash:
            fixed_indices[edge_hash[key]] = count

    free_indices = [i for i in range(len(unique_edges)) if i not in fixed_indices]
    edge_to_col = {idx: col for col, idx in enumerate(free_indices)}

    # Matrix A maps planes to their free edges
    matrix_a = np.zeros((len(polygon_objs), len(free_indices)), dtype=int)
    # Vector b stores the required parity based on fixed edges
    vector_b = np.zeros(len(polygon_objs), dtype=int)

    for p_idx, e_indices in enumerate(plane_to_edges):
        for e_idx in e_indices:
            if e_idx in fixed_indices:
                # Add fixed segment count to the plane's parity target
                vector_b[p_idx] = (vector_b[p_idx] + fixed_indices[e_idx]) % 2
            else:
                col = edge_to_col[e_idx]
                matrix_a[p_idx, col] = 1

    # --- 3. SOLVE AND ASSIGN ---
    # x_sol = 1 means odd (1 segment), x_sol = 0 means even (2 segments)
    x_sol = _solve_gf2(matrix_a, vector_b)

    edge_counts = np.zeros(len(unique_edges), dtype=int)
    for e_idx in range(len(unique_edges)):
        if e_idx in fixed_indices:
            edge_counts[e_idx] = fixed_indices[e_idx]
        else:
            col = edge_to_col[e_idx]
            edge_counts[e_idx] = 1 if x_sol[col] == 1 else 2

    return unique_edges, edge_counts
    
def _get_nodes(node1, node2, element_size, node_type, eps=0.01):
    """
    Generates evenly spaced nodes along an edge between two points.

    INPUTS:
    :param node1: Starting point (x, y, z) as array-like.
    :param node2: Ending point (x, y, z) as array-like.
    :param element_size: Target distance between nodes.
    :param node_type: 1 for odd number of total nodes (even segments), 
                      other for even number of total nodes (odd segments).
    
    RETURNS:
    :return: ndarray of shape (N, 3) representing node coordinates.
    """
    p1 = np.asarray(node1)
    p2 = np.asarray(node2)
    dist = np.linalg.norm(p2 - p1)
    
    if dist < eps:
        return p1[np.newaxis, :]

    # Calculate ideal segments (at least 1)
    segments = max(1, int(round(dist / element_size)))

    # Force parity: 
    # If node_type == 1, segments must be even.
    # If node_type != 1, segments must be odd.
    target_is_even = (node_type == 1)
    if (segments % 2 == 0) != target_is_even:
        segments += 1

    return np.linspace(p1, p2, segments + 1)
    
def mesh_polygons(polygon_objs, element_size, fixed_segments=None):
    """
    Complete workflow: 
    1. Solve topological parity.
    2. Generate nodes for every unique edge.
    3. Assemble continuous loops (outlines) for each polygon.
    """
    # 1. Determine the parity-consistent segment counts for each edge
    unique_edges, edge_counts = _det_edge_count(polygon_objs, fixed_segments)
    
    # Map edge keys back to indices for quick lookup during outline assembly
    edge_key_to_idx = {key: i for i, key in enumerate(unique_edges)}
    
    # 2. Assemble outlines for each polygon
    for p_idx, polygon_obj in enumerate(polygon_objs):
        outline_list = []
        loops = [polygon_obj.hull] + polygon_obj.holes
        
        # determine the completed outline list
        for loop in loops:
            outline = []
            n = len(loop)
            for i in range(n):
                p_start = loop[i]
                p_end = loop[(i + 1) % n]
                key = _get_edge_key(p_start, p_end)
                e_idx = edge_key_to_idx[key]
                
                # Retrieve pre-generated nodes for this edge
                node_type = edge_counts[e_idx]
                nodes =_get_nodes(p_start, p_end, element_size, node_type)
                
                outline.extend(nodes)
            
            outline_list.append(np.array(outline))

        # mesh outline list