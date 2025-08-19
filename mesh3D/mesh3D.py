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
        
    def search_byBox(self, x1, y1, z1, x2, y2, y3):
        element_nodes_coords = self.nodes[self.elements]
        elem_min = element_nodes_coords.min(axis=1)
        elem_max = element_nodes_coords.max(axis=1)

        mask = (
            (elem_max[:, 0] >= x1) & (elem_min[:, 0] <= x2) &
            (elem_max[:, 1] >= y1) & (elem_min[:, 1] <= y2) &
            (elem_max[:, 2] >= z1) & (elem_min[:, 2] <= z2)
        )
        return self.element_ids[mask]
    
    def normal(self, direction='+z'):
        dir_map = {
            '+x': np.array([1,0,0]),
            '-x': np.array([-1,0,0]),
            '+y': np.array([0,1,0]),
            '-y': np.array([0,-1,0]),
            '+z': np.array([0,0,1]),
            '-z': np.array([0,0,-1])
        }
        target_dir = dir_map[direction.lower()]

        coords = mesh.nodes[mesh.elements[:, :4]]        # bottom face coordinates
        v1 = coords[:, 1, :] - coords[:, 0, :]
        v2 = coords[:, 3, :] - coords[:, 0, :]
        normals = np.cross(v1, v2)
        
        dots = normals @ target_dir # @ is matrix multiplication / dot product in NumPy.
        flip_mask = dots < 0
        flip_indices = np.where(flip_mask)[0]

        # flip elements
        mesh.elements[flip_indices, :4] = mesh.elements[flip_indices, :4][:, ::-1]
        mesh.elements[flip_indices, 4:] = mesh.elements[flip_indices, 4:][:, ::-1]
        
def normalize_hex_direction(mesh, direction='+z'):
    """
    Reorient all 8-node hex elements along a specified direction.
    
    direction: one of '+x', '-x', '+y', '-y', '+z', '-z'
    """
    # map string to unit vector
    dir_map = {
        '+x': np.array([1,0,0]),
        '-x': np.array([-1,0,0]),
        '+y': np.array([0,1,0]),
        '-y': np.array([0,-1,0]),
        '+z': np.array([0,0,1]),
        '-z': np.array([0,0,-1])
    }
    
    target_dir = dir_map[direction.lower()]
    
    for i in range(len(mesh.elements)):
        elem = mesh.elements[i]
        # bottom face nodes
        n0, n1, n2, n3 = elem[:4]
        coords = mesh.nodes[[n0, n1, n2, n3]]
        
        # compute face normal
        v1 = coords[1] - coords[0]
        v2 = coords[3] - coords[0]
        normal = np.cross(v1, v2)
        
        # if normal is opposite to target direction, flip element
        if np.dot(normal, target_dir) < 0:
            # flip bottom nodes
            elem[:4] = elem[:4][::-1]
            # flip top nodes
            elem[4:] = elem[4:][::-1]
        
        mesh.elements[i] = elem