import numpy as np
import gc

def extract_faces_ultra_scale(elements):
    num_elements = elements.shape[0]
    # Represent "None" as the largest possible uint32
    UINT32_MAX = np.iinfo(np.uint32).max

    # 1. Local face map
    face_map = np.array([
        [0,1,2,3], [4,5,6,7], [0,1,5,4], 
        [1,2,6,5], [2,3,7,6], [3,0,4,7]
    ], dtype=np.uint32)

    all_faces = elements[:, face_map].reshape(-1, 4)
    element_ids = np.repeat(np.arange(num_elements, dtype=np.uint32), 6)

    # sort the node indices of each elements
    all_faces.sort(axis=1)

    # we cannot use standard Python sorting. We have to trick NumPy into 
    # treating each face as a single object rather than four separate numbers.
    faces_view = np.ascontiguousarray(all_faces).view(
        np.dtype((np.void, all_faces.dtype.itemsize * 4))
    ).ravel()
    
    sort_idx = np.argsort(faces_view)
    del faces_view
    gc.collect()

    # Identifying unique faces
    diff_mask = np.empty(len(sort_idx), dtype=bool)
    diff_mask[0] = True
    
    # Memory-safe comparison: compares chunks of the original array via indices
    # This avoids creating a sorted copy of all_faces (saves ~10GB)
    diff_mask[1:] = np.any(all_faces[sort_idx[1:]] != all_faces[sort_idx[:-1]], axis=1)
    
    unique_face_indices = sort_idx[diff_mask]
    shared_mask = ~diff_mask
    shared_mask[0] = False 

    # Mapping connectivity
    num_unique = len(unique_face_indices)
    
    # Initialize connectivity with UINT32_MAX instead of -1
    face_to_elems = np.full((num_unique, 2), UINT32_MAX, dtype=np.uint32)
    
    # Owner
    face_to_elems[:, 0] = element_ids[unique_face_indices]
    
    # Neighbor
    unique_id_map = np.cumsum(diff_mask).astype(np.uint32) - 1
    shared_face_ids = unique_id_map[shared_mask]
    face_to_elems[shared_face_ids, 1] = element_ids[sort_idx[shared_mask]]

    return face_to_elems, unique_face_indices

elements = np.array([
    [0,1,2,3,4,5,6,7],
    [4,5,6,7,8,9,10,11],
    [8,9,10,11,12,13,14,15],
    [12,13,14,15,16,17,18,19],
], dtype=np.uint32)

face_to_elems, unique_face_indices = extract_faces_ultra_scale(elements)

print(face_to_elems)