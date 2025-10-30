import numpy as np

def decouple(nodes, elements, z, dim, eps=1e-6):
    x1, y1, x2, y2 = dim
    xlo, xhi = (min(x1, x2) - eps, max(x1, x2) + eps)
    ylo, yhi = (min(y1, y2) - eps, max(y1, y2) + eps)

    ### find the target element, bottom element and upper element 
    en = nodes[elements]
    X, Y, Z = en[..., 0], en[..., 1], en[..., 2]

    z_mask   = np.abs(Z - z) < eps
    face_mask    = (X >= xlo) & (X <= xhi) & (Y >= ylo) & (Y <= yhi)
    touch_mask = np.any(z_mask & face_mask, axis=1)

    upper_mask = np.any(Z > z + eps, axis=1)
    upper_idx  = np.where(touch_mask & upper_mask)[0]
    
    bottom_mask = np.any(Z < z - eps, axis=1)
    bottom_idx = np.where(touch_mask & bottom_mask)[0]

    ### find nodes at the contact face
    node_x, node_y, node_z = nodes[:, 0], nodes[:, 1], nodes[:, 2]
    node_z_mask = np.abs(node_z - z) < eps
    node_face_mask  = (node_x >= xlo) & (node_x <= xhi) & (node_y >= ylo) & (node_y <= yhi)
    contact_node_mask = node_z_mask & node_face_mask
    contact_node_indices = np.where(contact_node_mask)[0]

    if contact_node_indices.size == 0 or upper_idx.size == 0:
        return nodes.copy(), elements.copy(), bottom_idx, upper_idx

    ### duplicate contact nodes
    new_nodes = nodes[contact_node_indices].copy()
    start_new_idx = len(nodes)
    new_indices = np.arange(start_new_idx, start_new_idx + contact_node_indices.size, dtype=elements.dtype)

    ### build old->new mapping array (default = identity)
    old_to_new = np.arange(len(nodes) + len(new_nodes), dtype=elements.dtype)
    old_to_new[contact_node_indices] = new_indices

    ### boolean mask for quick test whether an index is a contact node
    is_contact = np.zeros(len(nodes), dtype=bool)
    is_contact[contact_node_indices] = True

    ## remap only the upper-touching elements to the duplicated nodes
    E = elements[upper_idx]                 # view
    mask_contacts_in_E = is_contact[E]
    elements[upper_idx] = np.where(mask_contacts_in_E, old_to_new[E], E)
    nodes = np.vstack([nodes, new_nodes])

    return nodes, elements, bottom_idx, upper_idx
