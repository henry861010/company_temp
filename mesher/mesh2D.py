import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from my_math import *

import time
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

class Mesh2D:
    def __init__(self):
        ### process
        self.element_2D = np.empty((0, 4), dtype=np.int32)
        self.element_2D_nodes = np.empty((0), dtype=np.int32)
        self.node_2D = np.empty((0, 2), dtype=np.float32)
        
        ### others
        self.node_map = {}
        self.node_num = 0
        self.element_num = 0

    ### basic model building operation
    def add_node(self, x: float, y: float):
        node_key = f"{x}-{y}"
        if node_key not in self.node_map:
            new_node = np.array([[x, y]], dtype=np.float32)  # shape (1, 2)
            node_index = self.node_num
            self.node_2D[node_index] = new_node
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
        self.element_2D[element_index] = new_element
        self.element_num += 1
        
        return element_index

    def pre_allocate_nodes(self, size: int = 1):
        '''
        Exponential growth (1.5x) is a standard amortized allocation method (like Python lists or C++ vectors).
        This avoids frequent resizing for small additions, keeping total reallocation count logarithmic in size.
        Keeps allocation tight when near expected final size.
        '''
        required = self.node_num + size
        current_capacity = len(self.node_2D)
        if required > current_capacity:
            new_capacity = max(required, int(current_capacity * 1.5))
            extra = new_capacity - current_capacity
            self.node_2D = np.vstack([self.node_2D, np.empty((extra, 2), dtype=np.float32)])

    def pre_allocate_elements(self, size: int = 1):
        '''
        Exponential growth (1.5x) is a standard amortized allocation method (like Python lists or C++ vectors).
        This avoids frequent resizing for small additions, keeping total reallocation count logarithmic in size.
        Keeps allocation tight when near expected final size.
        '''
        required = self.element_num + size
        current_capacity = len(self.element_2D)
        if required > current_capacity:
            new_capacity = max(required, int(current_capacity * 1.5))
            extra = new_capacity - current_capacity
            self.element_2D = np.vstack([self.element_2D, np.empty((extra, 4), dtype=np.int32)])
        
    ### wrap operation
    def build_checkerboard(self, element_size, x_list, y_list, comp_id=0):
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
        nodes = np.column_stack([X.ravel(), Y.ravel()]).astype(np.float32)  # (Ny*Nx, 2)

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

        new_node_num = len(nodes)
        new_elem_num = len(elements)
        self.pre_allocate_elements(new_elem_num)
        self.pre_allocate_nodes(new_node_num)
        self.element_2D[self.element_num:self.element_num+new_elem_num+1] = elements
        self.node_2D[self.node_num:self.node_num+new_node_num+1] = nodes
        self.element_num += len(elements)
        self.node_num += len(nodes)

    ### access
    def get(self):
        element_coords = self.node_2D[:self.node_num][self.element_2D[:self.element_num]]
        element_node_ids = self.element_2D[:self.element_num]
        node_coords = self.node_2D[:self.node_num]
        node_ids = np.arange(self.node_2D.size, dtype=np.int32)
        
        return element_coords, element_node_ids, node_coords, node_ids

    ### debug
    def show_graph_2D(self, cmap='tab20'):
        patches = []
        colors = []

        coords = self.node_2D[:self.node_num][self.element_2D[:self.element_num]]#.reshape(-1, 2)  
        fig, ax = plt.subplots()
        pc = PolyCollection(
            coords, closed=True,
            facecolors='none', edgecolors='black', linewidths=1,
        )
        ax.add_collection(pc)

        ax.set_aspect('equal', adjustable='box')
        ax.autoscale()
        ax.grid(True)
        plt.show()