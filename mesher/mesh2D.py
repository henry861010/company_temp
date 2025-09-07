import numpy as np
import time
import math
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import utils
from utils.math import *
from utils.search_face import search_face_element, search_face_node

'''
    RULE:
    1. keep self.elements & self.nodes without empty
    NOTE:
    1. The delete_node() function is unnecessary. If nodes are deleted, elements may reference to 
    non-existent nodes. Moreover, nodes are only removed when deleting elements, this operation should 
    be handled exclusively within delete_element().
'''

ELEM_DIM = 4
NODE_DIM = 3

class Mesh2D:
    def __init__(self):
        ### process
        self.elements = np.empty((0, ELEM_DIM), dtype=np.int32)
        self.nodes = np.empty((0, NODE_DIM), dtype=np.float32)
        
        ### others
        self.node_map = {}
        self.node_num = 0
        self.element_num = 0
        
    def pre_allocate_nodes(self, size: int = 1):
        '''
        Exponential growth (1.5x) is a standard amortized allocation method (like Python lists or C++ vectors).
        This avoids frequent resizing for small additions, keeping total reallocation count logarithmic in size.
        Keeps allocation tight when near expected final size.
        '''
        required = self.node_num + size
        current_capacity = len(self.nodes)
        if required > current_capacity:
            new_capacity = max(required, int(current_capacity * 1.5))
            extra = new_capacity - current_capacity
            self.nodes = np.vstack([self.nodes, np.empty((extra, NODE_DIM), dtype=np.float32)])

    def pre_allocate_elements(self, size: int = 1):
        '''
        Exponential growth (1.5x) is a standard amortized allocation method (like Python lists or C++ vectors).
        This avoids frequent resizing for small additions, keeping total reallocation count logarithmic in size.
        Keeps allocation tight when near expected final size.
        '''
        required = self.element_num + size
        current_capacity = len(self.elements)
        if required > current_capacity:
            new_capacity = max(required, int(current_capacity * 1.5))
            extra = new_capacity - current_capacity
            self.elements = np.vstack([self.elements, np.empty((extra, ELEM_DIM), dtype=np.int32)])

    ### function
    def equivalence(self, eps=1e-8):
        elements = self.elements[:self.element_num]
        nodes = self.nodes[:self.node_num]
        new_elements, new_nodes = utils.equivalence(elements, nodes)
        
        self.elements  = new_elements
        self.element_num = len(new_elements)
        
        self.nodes  = new_nodes
        self.node_num = len(new_nodes)
                  
    ### wrap operation
    def mesh_checkerboard(self, element_size, x_list, y_list):
        # --- validate element_size ---
        if not np.isscalar(element_size) or float(element_size) <= 0:
            raise ValueError("element_size must be a positive scalar.")
        h = float(element_size)

        # --- normalize inputs ---
        x_list = np.asarray(x_list, dtype=np.float32).ravel()
        y_list = np.asarray(y_list, dtype=np.float32).ravel()
        if x_list.ndim != 1 or y_list.ndim != 1 or x_list.size < 2 or y_list.size < 2:
            raise ValueError("x_list and y_list must be 1D arrays with length >= 2.")

        # --- monotonic check ---
        if np.any(np.diff(x_list) < 0) or np.any(np.diff(y_list) < 0):
            raise ValueError("x_list and y_list must be non-decreasing.")

        # --- densify helper (handles zero-length spans) ---
        def densify(arr):
            out = []
            for a, b in zip(arr[:-1], arr[1:]):
                length = float(b - a)
                if length == 0.0:
                    # duplicate line: keep only one point when joining segments
                    if not out:
                        out.append(a)
                    continue
                nseg = max(1, int(np.ceil(length / h)))
                seg = np.linspace(a, b, nseg + 1, endpoint=True, dtype=np.float32)
                if out:
                    seg = seg[1:]  # avoid boundary duplicate
                out.extend(seg.tolist())
            return np.asarray(out, dtype=np.float32)

        x = densify(x_list)
        y = densify(y_list)
        if x.size < 2 or y.size < 2:
            raise ValueError("After densify, need at least 2 x-lines and 2 y-lines.")

        Nx, Ny = int(x.size), int(y.size)

        # --- nodes (x varies fastest) ---
        X, Y = np.meshgrid(x, y, indexing="xy")
        Z = np.zeros_like(X)
        nodes = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()]).astype(np.float32)  # (Ny*Nx, 2)

        # --- element node ids ---
        ix = np.arange(Nx - 1, dtype=np.int32)
        iy = np.arange(Ny - 1, dtype=np.int32)
        GX, GY = np.meshgrid(ix, iy, indexing="xy")

        n00 = (GY    ) * Nx + (GX    )  # BL
        n10 = (GY    ) * Nx + (GX + 1)  # BR
        n11 = (GY + 1) * Nx + (GX + 1)  # TR
        n01 = (GY + 1) * Nx + (GX    )  # TL

        # CLOCKWISE: BL, TL, TR, BR
        elements = np.stack([n00, n01, n11, n10], axis=-1).reshape(-1, 4).astype(np.int32)
        elements += self.node_num

        new_node_num = len(nodes)
        new_elem_num = len(elements)
        self.pre_allocate_elements(new_elem_num)
        self.pre_allocate_nodes(new_node_num)
        self.elements[self.element_num:self.element_num+new_elem_num+1] = elements
        self.nodes[self.node_num:self.node_num+new_node_num+1] = nodes
        self.element_num += len(elements)
        self.node_num += len(nodes)

    '''
        info_2D = {
            "model_type": "Full Model", "Half-x Model", "Half-y Model", "Quarter Model"
            "element_size":
            "element_type": 0:tri, 1:qual, 2:mixed, 4:qual only
            "algorithm": -
            "face_type":
            "face_dim":
            "pattern_info": {TYPE: []}
            "source_path":
            "cdb_source": 
            "cdb_target": 
            "outline_list":
        }
        
        info_3D = {
            
        }
        NOTE: The 3D drag could fully support by our Mesh3D, but the CoWoS-L model still required using HyperMesh
        to keep the same random metal assignment. the info3D would be remove in the next version 
    '''
    def mesh_HyperMesh(self, info_2D, info_3D=None, isHMagent=True):
        ### write to the template file
        ### NOTE: "if not info_3D: & inner command" temp for this version
        print(f"write 2D template (tcl)")
        info_2d_tcl = tcl(info_2d)
        if not info_3D:
             print(f"write 3D template (tcl)")
        
        ### write existed 2d mesh if necessary
        if self.element_num > 0:
            cdb_source = info_2D["cdb_source"]
            self.write(cdb_source)
            
        ### run hypermesh
        if isHMagent:
            print(f"request to HM agent")
        else:
            print(f"run cdb in local")
            
        ### import 2d back
        ### NOTE: "if not info_3D:" temp for this version
        if not info_3D:
            info_3d_tcl = tcl(info_3d)
            cdb_target = info_2D["cdb_target"]
            self.read(cdb_target)

    ### add
    def add_node(self, x: float, y: float):
        node_key = f"{x}-{y}"
        if node_key not in self.node_map:
            new_node = np.array([[x, y, 0]], dtype=np.float32)  # shape (1, 2)
            node_index = self.node_num
            self.nodes[node_index] = new_node
            self.node_map[node_key] = node_index
            self.node_num += 1
            return (node_index, x, y)
        else:
            return (self.node_map[node_key], x, y)

    def add_element(self, node1_dim: list, node2_dim: list, node3_dim: list, node4_dim: list, comp_id: int = 0):
        node1_index, node1_x, node1_y = self.add_node(*node1_dim)
        node2_index, node2_x, node2_y = self.add_node(*node2_dim)
        node3_index, node3_x, node3_y = self.add_node(*node3_dim)
        node4_index, node4_x, node4_y = self.add_node(*node4_dim)

        new_element = np.array([[node1_index, node2_index, node3_index, node4_index]], dtype=np.int32)  # shape (1, 10)

        element_index =  self.element_num
        self.elements[element_index] = new_element
        self.element_num += 1
        
        return element_index
        
    ### delete
    def delete_element(self, indices, isDeleteNode=True):
        if isinstance(indices,list):
            indices = np.array(indices, dtype=np.int32)
        
        ### delete the elements
        mask = np.ones(self.element_num, dtype=bool)
        mask[indices] = False
        self.elements = self.elements[mask]
        self.element_num -= len(indices)
        
        ### delete unreference node
        used_nodes = np.unique(self.elements)
        mapping = -np.ones(len(self.nodes), dtype=np.int32)
        mapping[used_nodes] = np.arange(len(used_nodes))
        self.elements = mapping[self.elements]
        self.nodes = self.nodes[used_nodes]
        self.node_num -= (self.node_num - len(used_nodes))
        
    ### search
    def search_element(self, type, dim, returnMask=False, isReverse=False):
        elements = self.elements[:self.element_num]
        nodes = self.nodes[:self.node_num]
        element_coordinates = nodes[elements][:,:,:2].reshape(elements.shape[0], -1)
        
        mask = search_face_element(element_coordinates, type, dim, returnMask=True)
        
        if isReverse:
            mask = ~mask
            
        if returnMask:
            return mask
        else:
            return np.flatnonzero(mask) 
    
    def search_node(self, type, dim, returnMask=False, isReverse=False):
        nodes = self.nodes[:self.node_num]
        mask = search_face_node(nodes, type, dim, returnMask=True)
    
        if isReverse:
            mask = ~mask
            
        if returnMask:
            return mask
        else:
            return np.flatnonzero(mask) 
    
    ### access
    '''
        return:
            1. nodes: coordinate of node [x, y, z]
            2. elements: each element incldue indice of node in nodes
            
    '''
    def get_byIndex(self):
        elements = self.elements[:self.element_num]
        nodes = self.nodes[:self.node_num]
        return nodes, elements

    '''
        return:
            1. node_ids: ids of nodes
            2. nodes: coordinate of node [x, y, z]
            3. element_ids: ids of elements
            4. elements: each element incldue id of node in nodes
            5. element_coords: coordinates of elements
    '''
    def get(self):
        elements = self.elements[:self.element_num]
        nodes = self.nodes[:self.node_num]
        
        node_ids = np.arange(1, self.node_num+1, dtype=np.int32)
        element_ids = np.arange(1, self.element_num+1, dtype=np.int32)
        element_coords = nodes[elements]
        elements_cdb = node_ids[elements]
        
        return node_ids, nodes, element_ids, elements_cdb, element_coords

    def get_outline(self):
        elements = self.elements[:self.element_num]
        nodes = self.nodes[:self.node_num]
        return utils.get_outline(elements , nodes)
    
    ### write CDB
    def write(self, path):
        print(f"write cdb (shell element)")
    
    ### debug
    def show_info(self):
        print("[nodes]")
        print(f"    nodes num: {self.node_num}({len(self.nodes)})")
        print("[2D element]")
        print(f"    elements num: {self.element_num}({len(self.elements)})")
        
    def show_graph_2D(self):
        coords = self.nodes[:self.node_num][self.elements[:self.element_num]]#.reshape(-1, 2)  
        fig, ax = plt.subplots()
        pc = PolyCollection(
            coords[:,:,:2], closed=True,
            facecolors='blue', edgecolors='black', linewidths=1,
        )
        ax.add_collection(pc)

        ax.set_aspect('equal', adjustable='box')
        ax.autoscale()
        plt.show()