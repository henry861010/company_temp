import numpy as np
import gc

def get_CFD_face(elements):
    num_elements = elements.shape[0]
    UINT32_MAX = np.iinfo(np.uint32).max

    face_map = np.array([
        [0,1,2,3], [4,5,6,7], [0,1,5,4], 
        [1,2,6,5], [2,3,7,6], [3,0,4,7]
    ], dtype=np.uint32)

    # all_faces holds the original winding order initially
    all_faces = elements[:, face_map].reshape(-1, 4)
    element_ids = np.repeat(np.arange(num_elements, dtype=np.uint32), 6)

    # To keep original winding, we need a sorted version for the 'key'
    # If memory is ultra-tight, we sort in-place as you did, 
    # but the face nodes returned will be in ascending order.
    # Let's assume you want the nodes as they appear in all_faces[unique_face_indices]
    
    # Create a sortable key without destroying the original winding
    # If RAM allows, use: sorted_keys = np.sort(all_faces, axis=1)
    # If RAM is critical, sort in-place (you lose the original normal direction)
    all_faces.sort(axis=1) 

    faces_view = np.ascontiguousarray(all_faces).view(
        np.dtype((np.void, all_faces.dtype.itemsize * 4))
    ).ravel()
    
    sort_idx = np.argsort(faces_view)
    del faces_view
    gc.collect()

    # Identifying unique faces
    diff_mask = np.empty(len(sort_idx), dtype=bool)
    diff_mask[0] = True
    diff_mask[1:] = np.any(all_faces[sort_idx[1:]] != all_faces[sort_idx[:-1]], axis=1)
    
    unique_face_indices = sort_idx[diff_mask]
    shared_mask = ~diff_mask
    shared_mask[0] = False 

    # Mapping connectivity
    num_unique = len(unique_face_indices)
    face_to_elems = np.full((num_unique, 2), UINT32_MAX, dtype=np.uint32)
    face_to_elems[:, 0] = element_ids[unique_face_indices]
    
    unique_id_map = np.cumsum(diff_mask).astype(np.uint32) - 1
    shared_face_ids = unique_id_map[shared_mask]
    face_to_elems[shared_face_ids, 1] = element_ids[sort_idx[shared_mask]]

    # RETRIEVING THE NODES:
    # These are the node IDs for each unique face.
    # If all_faces.sort() was used, these are sorted IDs.
    face_nodes = all_faces[unique_face_indices]

    return face_to_elems, face_nodes

def get_zone_grouped_indices(face_to_elems, element_comps):
    """
    Returns a list of arrays, where each array contains face indices 
    belonging to a unique component-pair zone.
    
        calssify the face to zone by element zone type
        1. Interior Zones: Faces where both elements belong to the same component (Comp A <-> Comp A).
        2. Interface/Jump Zones: Faces where elements belong to different components (Comp A <-> Comp B).
        3. Boundary Zones: Faces where the neighbor is UINT32_MAX. These are the external "skins" of your components.
    """
    UINT32_MAX = np.iinfo(np.uint32).max
    
    # 1. Map components
    owner_comps = element_comps[face_to_elems[:, 0]]
    neighbors = face_to_elems[:, 1]
    is_boundary = (neighbors == UINT32_MAX)
    
    neighbor_comps = np.full(len(neighbors), UINT32_MAX, dtype=np.uint32)
    neighbor_comps[~is_boundary] = element_comps[neighbors[~is_boundary]]

    # 2. Create Unique Zone Keys (Symmetric)
    # Pack two uint32 into one uint64
    c1 = np.minimum(owner_comps, neighbor_comps).astype(np.uint64)
    c2 = np.maximum(owner_comps, neighbor_comps).astype(np.uint64)
    zone_keys = (c1 << 32) | c2

    # 3. Sort indices by zone_keys
    # This brings all faces of the same zone together in memory
    sort_idx = np.argsort(zone_keys)
    sorted_keys = zone_keys[sort_idx]

    # 4. Find the split points (where the key changes)
    # np.flatnonzero returns indices where the condition is True
    change_points = np.flatnonzero(sorted_keys[1:] != sorted_keys[:-1]) + 1
    
    # 5. Split the sorted indices into a list of arrays
    # result is a list: [array([idx1, idx2...]), array([idx10, idx11...])]
    grouped_face_indices = np.split(sort_idx, change_points)

    # Optional: Get metadata for which zone is which
    unique_keys = sorted_keys[np.concatenate(([0], change_points))]
    zone_labels = []
    for key in unique_keys:
        a, b = np.uint32(key >> 32), np.uint32(key & 0xFFFFFFFF)
        label = f"Bnd_{a}" if b == UINT32_MAX else f"Int_{a}_{b}"
        zone_labels.append(label)

    return grouped_face_indices, zone_labels

def fix_face_winding(elements, nodes, face_nodes, face_to_elems):
    """
    elements: (N_elem, 8) uint32
    nodes: (N_nodes, 3) float64
    face_nodes: (N_faces, 4) uint32
    face_to_elems: (N_faces, 2) uint32
    
    The Logic for 100M Elements  To do this efficiently at scale, we use the Triple 
    Scalar Product:  Calculate a vector   v    from the Cell Centroid to the Face Centroid.  
    Calculate the Face Normal   n  using the cross product of two face edges. 
    If the dot product   v   ⋅  n   <0, the normal is pointing inward. We must flip 
    the node order 
    
    Fluent is very strict about Face Normals. For every face, the nodes must be ordered so the normal points from the Owner cell (Column 0) to the Neighbor cell (Column 1).
    For Internal faces, you may need to flip the face_node_indices for specific faces.
    For Boundary faces, the normal must point out of the domain.
    """
    # 1. Get Owner Cell Centroids
    # Centroid of a hex is the average of its 8 nodes
    # For 100M elements, this is the fastest way to get a reference interior point
    owner_indices = face_to_elems[:, 0]
    owner_cells = elements[owner_indices]
    # shape (N_faces, 8, 3) -> (N_faces, 3)
    cell_centroids = np.mean(nodes[owner_cells], axis=1)
    
    # 2. Get Face Centroids
    # For triangles, the 4th node index is usually a repeat or UINT32_MAX
    # We treat it as a quad for the mean; it doesn't affect the orientation check
    face_coords = nodes[face_nodes] # shape (N_faces, 4, 3)
    face_centroids = np.mean(face_coords, axis=1)
    
    # 3. Vector from Cell Centroid to Face Centroid (v)
    v = face_centroids - cell_centroids
    
    # 4. Calculate Face Normal (n)
    # n = (node1 - node0) x (node2 - node0)
    # We use nodes 0, 1, and 2 of the face
    edge1 = face_coords[:, 1, :] - face_coords[:, 0, :]
    edge2 = face_coords[:, 2, :] - face_coords[:, 0, :]
    face_normals = np.cross(edge1, edge2)
    
    # 5. Check Orientation
    # dot_product = v . n
    dot_product = np.einsum('ij,ij->i', v, face_normals)
    
    # Faces where dot_product < 0 need flipping
    flip_mask = dot_product < 0
    
    # 6. Flip the nodes in-place (Swap index 1 and 3)
    # [n0, n1, n2, n3] becomes [n0, n3, n2, n1]
    # This reverses the winding without changing the starting node
    face_nodes[flip_mask, 1], face_nodes[flip_mask, 3] = \
        face_nodes[flip_mask, 3].copy(), face_nodes[flip_mask, 1].copy()
        
    return face_nodes

def FEM_to_CFD(femMeshData: 'FemMeshData'):
    # get the face
    face_to_elems, face_node_indices = get_CFD_face(femMeshData.elements)


elements = np.array([
    [0,1,2,3,4,5,6,7],
    [4,5,6,7,8,9,10,11],
    [8,9,10,11,12,13,14,15],
    [12,13,14,15,16,17,18,19],
], dtype=np.uint32)

element_comps =  np.array([
    0,1,0,1
], dtype=np.uint32)

face_to_elems, face_nodes = get_CFD_face(elements)

grouped_face_indices, zone_labels = get_zone_grouped_indices(face_to_elems, element_comps)

print(grouped_face_indices)

print(zone_labels)
