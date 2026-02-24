import numpy as np

def extract_mesh_topology_fast(elements):
    num_elements = elements.shape[0]
    face_map = np.array([
        [0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], 
        [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]
    ])

    # 1. Generate all faces and track their parent element
    all_faces = elements[:, face_map].reshape(-1, 4)
    element_ids = np.repeat(np.arange(num_elements, dtype=np.int32), 6)

    # 2. Sort nodes within each face to create a "key"
    sorted_faces = np.sort(all_faces, axis=1)

    # 3. Create a structured view for fast row-wise comparison
    # We treat the 4 integers as a single 16-byte object
    dtype = np.dtype((np.void, sorted_faces.dtype.itemsize * sorted_faces.shape[1]))
    sorted_view = np.ascontiguousarray(sorted_faces).view(dtype).ravel()

    # 4. Sort the entire list of faces by their "keys"
    sort_indices = np.argsort(sorted_view)
    sorted_view = sorted_view[sort_indices]
    
    # 5. Identify unique faces and where duplicates exist
    # diff_mask marks the start of every NEW unique face
    diff_mask = np.concatenate(([True], sorted_view[1:] != sorted_view[:-1]))
    unique_face_indices = sort_indices[diff_mask]
    
    # Count how many times each unique face appears
    # (1 = boundary, 2 = internal shared)
    face_counts = np.diff(np.append(np.flatnonzero(diff_mask), len(sorted_view)))
    
    # 6. Build the connectivity array
    num_unique = len(unique_face_indices)
    face_to_elems = np.full((num_unique, 2), -1, dtype=np.int32)
    
    # The first element sharing the face is always at the diff_mask positions
    face_to_elems[:, 0] = element_ids[sort_indices[diff_mask]]
    
    # The second element only exists where count == 2
    # These elements are located at (indices of diff_mask) + 1
    shared_mask = face_counts == 2
    shared_indices = sort_indices[np.flatnonzero(diff_mask)[shared_mask] + 1]
    face_to_elems[shared_mask, 1] = element_ids[shared_indices]

    unique_faces = all_faces[unique_face_indices]
    return unique_faces, face_to_elems

elements = np.array([
    [0,1,2,3,4,5,6,7],
    [4,5,6,7,8,9,10,11],
    [8,9,10,11,12,13,14,15],
    [12,13,14,15,16,17,18,19],
], dtype=np.int32)

unique_faces, face_to_elems = extract_mesh_topology_fast(elements)

print(unique_faces)
print(face_to_elems)