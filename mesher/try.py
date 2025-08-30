import numpy as np
elem2D_nodes = np.array([[1,2,3], [3,2,1], [2,1,2]], np.int32)
node2D_idx, inv = np.unique(elem2D_nodes, return_inverse=True)

print(node2D_idx)
print(inv)