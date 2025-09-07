import numpy as np
from matplotlib.path import Path

def search_face_element(element_coordinates, type, dim, index=None, eps=0.0, returnMask=False):
    """
        Fast predicate on subset indices (index). 
        Returns a boolean mask aligned to index (or to all rows if index is None).
    """
    rows = index if index is not None else np.arange(len(element_coordinates))

    # gather 4 corners
    cols = np.array([0, 2, 4, 6], dtype=int)
    x4 = element_coordinates[np.ix_(rows, cols)]
    cols = np.array([1, 3, 5, 7], dtype=int)
    y4 = element_coordinates[np.ix_(rows, cols)]
    
    ### max/min of each element_coordinates
    min_x = x4.min(axis=1)
    max_x = x4.max(axis=1)
    min_y = y4.min(axis=1)
    max_y = y4.max(axis=1)

    if type == "BOX":
        bl_x, bl_y, tr_x, tr_y = dim
        if eps:
            bl_x -= eps
            bl_y -= eps
            tr_x += eps
            tr_y += eps
        res_mask = (min_x >= bl_x) & (max_x <= tr_x) & (min_y >= bl_y) & (max_y <= tr_y)

    elif type == "CYLINDER":
        cx, cy, r = dim
        rr = r*r + 0.0
        if eps:
            rr = (r + eps) * (r + eps)
        dist = (x4 - cx)**2 + (y4 - cy)**2
        res_mask = np.all(dist <= rr, axis=1)
    
    elif type == "POLYGON":
        radiu = -1e-12
        path = Path(np.asarray(dim, float))
        
        node1_list = element_coordinates[:, [0, 1]]
        mask1 = path.contains_points(node1_list, radius=radiu)

        node2_list = element_coordinates[:, [2, 3]]
        mask2 = path.contains_points(node2_list, radius=radiu)
        
        node3_list = element_coordinates[:, [4, 5]]
        mask3 = path.contains_points(node3_list, radius=radiu)
        
        node4_list = element_coordinates[:, [6, 7]]
        mask4 = path.contains_points(node4_list, radius=radiu)
        res_mask = mask1 & mask2 & mask3 & mask4
    else:
        raise ValueError(f"Unsupported type: {type}")
    
    if returnMask:
        return res_mask
    else:
        return np.flatnonzero(res_mask) 
    
def search_face_node(nodes, type, dim, index=None, eps=0.0, returnMask=False):
    """
        Fast predicate on subset indices (index). 
        Returns a boolean mask aligned to index (or to all rows if index is None).
    """
    if type == "BOX":
        if eps:
            bl_x -= eps
            bl_y -= eps
            tr_x += eps
            tr_y += eps
        res_mask = (nodes[:,0] >= bl_x) & (nodes[:,1] <= tr_x) & (nodes[:,0] >= bl_y) & (nodes[:,1] <= tr_y)

    elif type == "CYLINDER":
        cx, cy, r = dim
        rr = r*r + 0.0
        if eps:
            rr = (r + eps) * (r + eps)
        dist = (nodes[:,0] - cx)**2 + (nodes[:,1] - cy)**2
        res_mask = dist <= rr
    
    elif type == "POLYGON":
        radiu = -1e-12
        path = Path(np.asarray(dim, float))
        res_mask = path.contains_points(nodes, radius=radiu)
        
    else:
        raise ValueError(f"Unsupported type: {type}")
    
    if returnMask:
        return res_mask
    else:
        return np.flatnonzero(res_mask) 