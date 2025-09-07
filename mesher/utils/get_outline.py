import numpy as np

def get_outline(elements: np.ndarray, nodes: np.ndarray):
    if elements.size == 0:
        return []

    # If elements are 1-based, normalize to 0-based (detect quickly).
    if elements.min() == 1 and elements.max() <= nodes.shape[0]:
        elems = elements - 1
    else:
        elems = elements

    # Build all edges (undirected) for quads: (n0-n1, n1-n2, n2-n3, n3-n0)
    e0 = elems[:, [0, 1]]
    e1 = elems[:, [1, 2]]
    e2 = elems[:, [2, 3]]
    e3 = elems[:, [3, 0]]
    all_edges = np.vstack([e0, e1, e2, e3])
    all_edges = all_edges[all_edges[:,0] != all_edges[:,1]]

    # Keep a copy with original direction (for possible orientation needs),
    # but use a sorted version to detect duplicates
    undirected = np.sort(all_edges, axis=1)

    # Unique edges and their multiplicity
    # counts==1 => boundary edges; counts==2 => interior edges
    uniq, inv, counts = np.unique(undirected, axis=0, return_inverse=True, return_counts=True)
    boundary_mask = (counts[inv] == 1)
    boundary_edges = all_edges[boundary_mask]                  # use original endpoints

    ### mapping table
    ### map_src a->b
    ### map_end b->a
    ### count a-b used
    map_src_to_end = {int(s): int(e) for s, e in boundary_edges}
    map_end_to_src = {int(e): int(s) for s, e in boundary_edges}
    
    outline_list = []
    while len(map_src_to_end):
        first_index = next(iter(map_src_to_end))
        outline = [first_index]
        
        pre_index = first_index
        next_index = map_src_to_end[first_index]

        del map_src_to_end[first_index]
        del map_end_to_src[first_index]
        
        while first_index != next_index:
            outline.append(next_index)
            now_index = next_index
            
            ### find the next index
            next1_index = map_src_to_end[now_index]
            next2_index = map_end_to_src[now_index]
            if next1_index != pre_index:
                next_index = next1_index
            else:
                next_index = next2_index
                
            ### remove the now
            del map_src_to_end[now_index]
            del map_end_to_src[now_index]
            
            ### set for next round
            pre_index = now_index
            
        outline_list.append(outline)
        
    return outline_list, nodes[outline_list]
            
            
    