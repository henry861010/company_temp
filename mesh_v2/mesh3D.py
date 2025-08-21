import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from my_math import *

import time
from test.test_util import *

'''
    element_2D: [
        {
            element_id,
            comp_id,
            area,
            node1_x, node1_y,
            node2_x, node2_y,
            node3_x, node3_y,
            node4_x, node4_y
        }
    ]
    element_2D: [
        {
            element_id,
            comp_id,
            area,
            node1_x, node1_y,
            node2_x, node2_y,
            node3_x, node3_y,
            node4_x, node4_y
        }
    ]
    element_2D_nodes: [
        {
            node1_id
            node2_id
            node3_id
            node4_id
        }
    ]
    element_areas: [
        area
    ]

    nodes: [
        {
            node_x, 
            node_y
        }
    ]
    node_map: {}
        f"{x}-{y}" -> node_id
    materials: [
        material_name
    ]
    set: [
        {
            name: name
            ids: []
        }
    ]
    
    area: {
        material
        ranges: [
            {
                type: BOX/CONE
                dim: []
            }
        ]
        holes: [
            {
                type: BOX/CONE
                dim: []
            }
        ]
        metals: [
            {
                material
                type: NORMAL / CONTINUE
                density: 
            }
        ]
    }
'''
ELEMENT_ID = 0
ELEMENT_COMP_ID = 1
ELEMENT_AREA = 2
ELEMENT_NODE1_X = 3
ELEMENT_NODE1_Y = 4
ELEMENT_NODE2_X = 5
ELEMENT_NODE2_Y = 6
ELEMENT_NODE3_X = 7
ELEMENT_NODE3_Y = 8
ELEMENT_NODE4_X = 9
ELEMENT_NODE4_Y = 10
ELEMENT_len = 11

CDB_COMP_ELEM_PER_LINE = 8

class Mesh3D:
    def __init__(self, element_2D = None, node_2D = None, element_2D_nodes = None, x_list = None, y_list = None):
        ### property
        self.material_table = {"EMPTY": 0}
        self.element_3D = np.empty((0, 9), dtype=np.int32)
        self.node_3D = np.empty((0, 3), dtype=np.int32)
        
        ### process
        self.element_2D = np.empty((0, ELEMENT_len), dtype=np.float32)
        self.element_2D_nodes = np.empty((0, 4), dtype=np.int32)
        self.node_2D = np.empty((0, 2), dtype=np.float32)
        
        self.z_table = [0]
        
        ### [initial method 1] node_2D & element_2D_nodes [[node1, node2, node3, node4]]
        if node_2D is not None and element_2D_nodes is not None:
            ### init self.node_2D
            self.node_2D = node_2D
            n = element_nodes.shape[0]
            
            ### init element_2D_nodes
            self.element_2D_nodes = element_2D_nodes

            ### init self.element_2D
            self.element_2D = np.zeros((n, 11), dtype=np.float32)
            self.element_2D[:, 0] = np.arange(n)
            for i in range(4):
                self.element_2D[:, 3 + 2 * i]     = node_2D[element_nodes[:, i], 0]
                self.element_2D[:, 3 + 2 * i + 1] = node_2D[element_nodes[:, i], 1]
                
        ### [initial method 2] block ~ x_list, y_list
        if x_list is not None and y_list is not None:
            self.mesh_2D_block(x_list, y_list)
        
    def mesh_2D_block(self, x_list, y_list):
        # Convert x_list and y_list to arrays
        x_num = len(x_list)
        y_num = len(y_list)
        element_num = (x_num - 1) * (y_num - 1)
        y_list_np = np.array(y_list)
        
        ### declare 
        self.node_2D = np.zeros((x_num * y_num, 2), dtype=np.float32) 
        self.element_2D = np.zeros((element_num, 11), dtype=np.float32) 
        self.element_2D_nodes = np.zeros((element_num, 4), dtype=np.int32) 
        
        element_nodes_list = np.array([[i-1, i] for i in range(1, y_num)])
        
        for index, x in enumerate(x_list):
            ### build self.node_2D
            self.node_2D[index * y_num : (index + 1) * y_num, 1] = y_list_np
            self.node_2D[index * y_num : (index + 1) * y_num, 0] = np.zeros(y_num, dtype=np.float32) + x

            ### build self.element_2D_nodes
            if index > 0:
                start = (index - 1) * (y_num - 1)
                end = index * (y_num - 1)
                self.element_2D_nodes[start:end] = np.hstack((
                    element_nodes_list,
                    element_nodes_list + y_num
                ))
                element_nodes_list += y_num
                
        ### build self.element_2D
        coords = self.node_2D[self.element_2D_nodes]
        self.element_2D[:, 3:11] = coords.reshape(element_num, 8)
        
    def organize(self, area: dict):
        # AND each "range" constraint (element must satisfy all range boxes)
        start = time.time()
        range_masks = []
        for range_info in area["ranges"]:
            if range_info["type"] == "BOX":
                range_masks.append(
                    (self.element_2D[:, ELEMENT_NODE1_X] >= range_info["dim"][0]) &
                    (self.element_2D[:, ELEMENT_NODE1_Y] >= range_info["dim"][1]) &
                    (self.element_2D[:, ELEMENT_NODE3_X] <= range_info["dim"][2]) &
                    (self.element_2D[:, ELEMENT_NODE3_Y] <= range_info["dim"][3])  
                )
        if len(range_masks) > 0:
            target_elements = self.element_2D[np.logical_or.reduce(range_masks)]

        # Exclude any that intersect with a hole
        hole_masks = []
        for hole_info in area["holes"]:
            if hole_info["type"] == "BOX":
                hole_masks.append(
                    ~((target_elements[:, ELEMENT_NODE1_X] >= hole_info["dim"][0]) &
                    (target_elements[:, ELEMENT_NODE1_Y] >= hole_info["dim"][1]) &
                    (target_elements[:, ELEMENT_NODE3_X] <= hole_info["dim"][2]) &
                    (target_elements[:, ELEMENT_NODE3_Y] <= hole_info["dim"][3]))
                )
        if len(hole_masks) > 0:
            target_elements = target_elements[np.logical_and.reduce(hole_masks)]
        
        ### calculate the area
        total_area = target_elements[:, ELEMENT_AREA].sum()
        
        ### assign the metal "CONTINUE"
        exclude_masks = []
        for metal_info in area["metals"]:
            if metal_info["type"] == "CONTINUE":
                ### the assigned material
                comp_id = self.material_table[metal_info["material"]]
                
                ### find the material with same materal as assigned
                exclude_masks.append(
                    ~(target_elements[:, ELEMENT_COMP_ID] == comp_id)
                )
        if len(exclude_masks) > 0:
            target_elements = target_elements[np.logical_and.reduce(exclude_masks)]
        
        ### assign the metal "NORMAL"
        ### NOTE: np.random.shuffle is very slow!!!
        if len(area["metals"]) > 0:
            np.random.seed(1)
            np.random.shuffle(target_elements)
            index = len(target_elements) - 1
            for metal_info in area["metals"]:
                if metal_info["type"] == "NORMAL":
                    ### the assigned material
                    if not metal_info["material"] in self.material_table:
                        new_comp_id = len(self.material_table)
                        self.material_table[metal_info["material"]] = new_comp_id
                    comp_id = self.material_table[metal_info["material"]]
                    
                    ### begin to assign the metal
                    seleted_area = 0
                    temp_count = 0
                    while index >= 0 and (seleted_area / total_area) < metal_info["density"]/100:
                        seleted_area += target_elements[index][ELEMENT_AREA]
                        element_id = int(target_elements[index][ELEMENT_ID])
                        self.element_2D[element_id][ELEMENT_COMP_ID] = comp_id
                        index -= 1
                        temp_count += 1
            ### the index ~ end was assigned and should be remove from target_elements 
            target_elements = target_elements[0 : index + 1]
                    
        ### assign the material
        if not area["material"] in self.material_table:
            new_comp_id = len(self.material_table)
            self.material_table[area["material"]] = new_comp_id
        target_element_index = target_elements[:, ELEMENT_ID].astype(int)
        self.element_2D[target_element_index, ELEMENT_COMP_ID] = self.material_table[area["material"]]
        
    def drag(self, element_size: float, end: float):
        z_now = self.z_table[-1]
        distance = end - z_now
        on_drag = math.ceil(distance / element_size)
        
        # Adjust element size if not evenly divisible
        if f_ne(on_drag, distance / element_size):
            element_size = distance / on_drag

        # Step 1: Get non-empty 2D elements
        non_empty_mask = self.element_2D[:, ELEMENT_COMP_ID] != 0
        element_comp_list = self.element_2D[non_empty_mask][:, ELEMENT_COMP_ID]
        element_nodes_list = self.element_2D_nodes[non_empty_mask]

        k = len(element_comp_list)
        if k == 0:
            return  # No elements to extrude

        # Step 2: Precompute all extruded elements
        original_node_count = len(self.node_2D)
        all_new_elements = []

        for i in range(on_drag):
            offset = i * original_node_count
            lower_nodes = element_nodes_list + offset
            upper_nodes = element_nodes_list + offset + original_node_count
            merged = np.hstack((element_comp_list[:, None], lower_nodes, upper_nodes)).astype(int)  # (k, 9)
            all_new_elements.append(merged)

        all_new_elements = np.vstack(all_new_elements)  # (k * on_drag, 9)
        self.element_3D = np.vstack((self.element_3D, all_new_elements))
        
        # Step 4: Update z_table
        new_rows = [z_now + (i+1) * element_size for i in range(on_drag)]
        self.z_table += new_rows

    ### Searching
    def cal_areas(self):
        # Extract coordinates as (N, 4) for each x and y
        x1, y1 = self.element_2D[:, ELEMENT_NODE1_X],  self.element_2D[:, ELEMENT_NODE1_Y]
        x2, y2 = self.element_2D[:, ELEMENT_NODE2_X],  self.element_2D[:, ELEMENT_NODE2_Y]
        x3, y3 = self.element_2D[:, ELEMENT_NODE3_X],  self.element_2D[:, ELEMENT_NODE3_Y]
        x4, y4 = self.element_2D[:, ELEMENT_NODE4_X],  self.element_2D[:, ELEMENT_NODE4_Y]

        # Shoelace formula for quadrilateral
        areas = 0.5 * np.abs(
            x1*y2 + x2*y3 + x3*y4 + x4*y1 -
            (y1*x2 + y2*x3 + y3*x4 + y4*x1)
        )

        # Store back into column 13
        self.element_2D[:, ELEMENT_AREA] = areas
        
    def search(self, type: str, node1_x:float, node1_y:float, node1_z:float, node3_x:float, node3_y:float, node3_z:float, tolerance: float = 0.0001):
        print("~~~~~")
        
    ### CDB format
    def renumber(self):
        ### Flatten all node references in element data, and get the unique id
        ref_node_ids = self.element_3D[:, 1:9].ravel()
        used_node_ids = np.unique(ref_node_ids)

        # renumber the element id
        node_id_table = np.full(self.node_2D.shape[0] * len(self.z_table), -1, dtype=np.int32)
        node_id_table[used_node_ids] = np.arange(len(used_node_ids))
        self.element_3D[:, 1:9] = node_id_table[self.element_3D[:, 1:9]]

        ### Step 2: Build the full 3D node array 
        xy_repeated = np.tile(self.node_2D, (len(self.z_table), 1))
        z_repeated = np.repeat([z for z in self.z_table], len(self.node_2D))[:, np.newaxis]
        node_3D_full = np.hstack((xy_repeated, z_repeated))
        self.node_3D = node_3D_full[used_node_ids]
        
    def merge(self, obj2: 'Mesh3D', interfaces: list = None):
        if interfaces is None:
            # 1. Extract all used node IDs
            ids_1 = np.unique(self.element_3D_1[:, 1:])
            ids_2 = np.unique(self.element_3D_2[:, 1:])

            coords_1 = self.node_3D[ids_1]
            coords_2 = self.node_3D[ids_2]

            # 2. Combine both and find unique coordinates with deduplication
            all_coords = np.vstack((coords_1, coords_2))
            all_ids = np.hstack((ids_1, ids_2))

            # Round coordinates to avoid float precision issues (optional but safer)
            rounded = np.round(all_coords, decimals=6)

            # 3. Use np.unique to find shared nodes and get canonical index
            unique_coords, inverse_indices = np.unique(rounded, axis=0, return_inverse=True)

            # Build final mapping from original node id → unified id
            # We assign priority to ids_1 by keeping the first occurrence
            _, first_occurrence_indices = np.unique(inverse_indices, return_index=True)
            canonical_ids = all_ids[first_occurrence_indices]  # shape (len(unique_coords),)

            # 4. Build full mapping table: original id → canonical id
            mapping_table = np.full(self.node_3D.shape[0], -1, dtype=np.int32)
            mapping_table[all_ids] = canonical_ids[inverse_indices]

            # 5. Remap element_3D_2
            self.element_3D_2[:, 1:] = mapping_table[self.element_3D_2[:, 1:]]
        else:
            for interface in interfaces:
                
    def read_CDB(self):
        print("~")
         
    def generate_cdb(self, path: str = 'cdb.txt', element_type: str = "185"):
        print("generate CDB")
        
    def show_info(self):
        ### basic info
        print(f"[Basic Info]:")
        print(f"    total 2D elems: {len(self.element_2D)}")
        print(f"    total 3D elems: {len(self.element_3D)}")
        ### comp info
        print(f"[COMP info]:")
        for material, comp_id in self.material_table.items():
            elements = self.element_2D[self.element_2D[:, ELEMENT_COMP_ID] == comp_id]
            print(f"    {material}: {len(elements)} items")