import numpy as np
'''
    element: [node1, node2, ... ,node8]
    element_id: id
    node: [x, y, z]
    
'''

class ParserFEM:
    def __init__(self):
        self.elements = np.empty((0, 8), dtype=int32)
        self.element_ids = np.empty((0), dtype=int32)
        self.nodes = np.empty((0, 3), dtype=float64)
        self.node_ids = np.empty((0), dtype=int32)
    
    def read_CDB(self, path: str):
        print("read CDB")
        
    def write(self, path: str):
        print("write CDB")
        
    def set_FEM(self, elements, ids, nodes):
        self.elements = elements
        self.ids = ids
        self.nodes = nodes
        
    def get_FEM(self):
        return self.elements, self.ids, self.nodes
    
class Mesh3D(self):
    def __init__(self):
        self.elements = np.empty((0, 8), dtype=int32)
        self.element_ids = np.empty((0), dtype=int32)
        self.nodes = np.empty((0, 3), dtype=float64)
        self.node_ids = np.empty((0), dtype=int32)
    
    def renumber(self):
        # Step 1: sort nodes by z
        node_index = np.argsort(self.nodes[:, 2])  # indices that sort nodes by z

        # Step 2: create mapping from old index -> new index
        new_index = np.empty_like(node_index)
        new_index[node_index] = np.arange(len(node_index))

        # Step 3: reorder nodes
        self.nodes = self.nodes[node_index]

        # Step 4: assign continuous node IDs (1,2,3,...)
        self.node_ids = np.arange(1, len(self.nodes) + 1)

        # Step 5: update element connectivity to use new node indices
        # Note: subtract 1 to convert to 0-based index for array
        self.elements = new_index[self.elements]

        # Step 6: assign continuous element IDs (1,2,3,...)
        self.element_ids = np.arange(1, len(self.elements) + 1)
        
    def normal(self, direction):
        mapping = {
            "+z": {
                "+x": [0,4,5,1,3,7,6,2],
                "-x": [0,4,7,3,1,5,6,2],
                "+y": [0,3,7,4,1,2,6,5],
                "-y": [0,1,5,4,3,2,6,7],
                "+z": [0,1,2,3,4,5,6,7],
                "-z": [0,3,2,1,4,7,6,5],
            },
            "-z": {
                "+x": [0,1,5,4,3,2,6,7],
                "-x": [0,3,7,4,1,2,6,5],
                "+y": [0,4,7,3,1,5,6,2],
                "-y": [0,4,5,1,3,7,6,2],
                "+z": [0,3,2,1,4,7,6,5],
                "-z": [0,1,2,3,4,5,6,7],
            }
        }

        # bottom face coordinates
        coords = self.nodes[self.elements[:, :4]]        # (n_elem,4,3)
        v1 = coords[:, 1, :] - coords[:, 0, :]
        v2 = coords[:, 3, :] - coords[:, 0, :]
        normals = np.cross(v1, v2)                       # (n_elem,3)

        # normalize
        lengths = np.linalg.norm(normals, axis=1, keepdims=True)
        lengths[lengths == 0] = 1.0
        normals = normals / lengths

        # loop through all axes
        for axis, sign in [(0, 1), (0, -1), (1, 1), (1, -1), (2, 1), (2, -1)]:
            idx = np.where(normals[:, axis] == sign)[0]
            if len(idx) == 0:
                continue
            if axis == 0:  # x-axis
                key = "+x" if sign == 1 else "-x"
            elif axis == 1:  # y-axis
                key = "+y" if sign == 1 else "-y"
            else:  # z-axis
                key = "+z" if sign == 1 else "-z"
            self.elements[idx, :] = self.elements[idx][:, mapping[direction][key]]

    def bounding_box(self, mask=None):
        if mask is None:
            element_coords = self.nodes[self.elements]
        else:
            element_coords = self.nodes[self.elements[mask]]
        min_x = np.min(element_coords[:,:, 0])
        min_y = np.min(element_coords[:,:, 1])
        min_z = np.min(element_coords[:,:, 2])
        max_x = np.max(element_coords[:,:, 0])
        max_y = np.max(element_coords[:,:, 1])
        max_z = np.max(element_coords[:,:, 2])
        return [min_x, min_y, min_z, max_x, max_y, max_z]
    