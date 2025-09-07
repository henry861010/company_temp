import numpy as np

def equivalence(elements, nodes, eps=1e-8):
    nodes = np.asarray(nodes, dtype=np.float64, order='C')
    elements = np.asarray(elements, order='C')

    # Quantize
    qx = np.round(nodes[:, 0] / eps).astype(np.int64, copy=False)
    qy = np.round(nodes[:, 1] / eps).astype(np.int64, copy=False)
    qz = np.round(nodes[:, 2] / eps ).astype(np.int64, copy=False)
    
    # Sort by (qz, qx, qy)
    order = np.lexsort((qy, qx, qz))  # primary is last key => qz, then qx, then qy
    qz_s = qz[order]; qx_s = qx[order]; qy_s = qy[order]

    # Run-length unique over sorted triples
    same_as_prev = np.zeros(qz_s.shape[0], dtype=bool)
    same_as_prev[1:] = (qz_s[1:] == qz_s[:-1]) & (qx_s[1:] == qx_s[:-1]) & (qy_s[1:] == qy_s[:-1])
    group_id_sorted = np.cumsum(~same_as_prev) - 1  # 0..n_unique-1

    # Invert sorting to get "inverse" mapping for original node order
    inv_order = np.empty_like(order)
    inv_order[order] = np.arange(order.size, dtype=order.dtype)
    inverse = group_id_sorted[inv_order].astype(np.int32, copy=False)

    # Extract unique nodes (keep first occurrence)
    unique_mask_sorted = ~same_as_prev
    unique_nodes = nodes[order[unique_mask_sorted]].astype(np.float32, copy=False)

    # Remap elements IN-PLACE (no extra big allocation)
    np.take(inverse, elements, out=elements)

    return elements, unique_nodes