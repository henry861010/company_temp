import numpy as np

def find_face(nodes, elements):
    '''
        face1: 1432 -> 0321
        face2: 1265 -> 0154
        face3: 2376 -> 1265
        face4: 3487 -> 2376
        face5: 1584 -> 0473
        face6: 5678 -> 4567
        
        hexahedron, Prism, Tetrahedral, and Pyramid
    '''
    faces1 = elements[:,[0,3,2,1]]
    faces2 = elements[:,[0,1,5,4]]
    faces3 = elements[:,[1,2,6,5]]
    faces4 = elements[:,[2,3,7,6]]
    faces5 = elements[:,[0,4,7,3]]
    faces6 = elements[:,[4,5,7,6]]
    
    faces = np.vstack([faces1, faces2, faces3, faces4, faces5, faces6])
    sorted_faces = np.sort(faces, axis=1)
    
    # find the face where it have 3 or 4 non-duplicate node
    is_same = (sorted_faces[:,1:] - sorted_faces[:,:-1])
    non_dup = np.sum(is_same, axis=1)
    valid_mask = non_dup >= 3
    faces = faces[valid_mask]
    
    # Count multiplicity on undirected edges -> boundary = multiplicity == 1
    uniq, inv, counts = np.unique(faces, axis=0, return_inverse=True, return_counts=True)
    boundary_mask = (counts[inv] == 1)
    boundary_faces = faces[boundary_mask]
    
    return boundary_faces
    