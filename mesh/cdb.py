import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from my_math import *

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
    element_to_nodes: [
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

class CDB:
    def __init__(self):
        self.components = [] ### [component_name, ... ]
        self.element_2D = np.empty((0, ELEMENT_len), dtype=np.float32)
        self.element_3D = []
        self.element_to_nodes = np.empty((0, 4), dtype=np.int32)
        self.nodes = np.empty((0, 2), dtype=np.float32)
        self.node_map = {}
        self.material_table = {"EMPTY": 0}
        self.z_table = [0]
        
        self.sets = []

    ### basic model building operation
    def add_node(self, x: float, y: float):
        node_key = f"{x}-{y}"
        if node_key not in self.node_map:
            new_node = np.array([[x, y]], dtype=np.float32)  # shape (1, 2)
            self.nodes = np.vstack([self.nodes, new_node])
            node_id = len(self.nodes) - 1
            self.node_map[node_key] = node_id
            return (node_id, x, y)
        else:
            return (self.node_map[node_key], x, y)

    def add_element(self, node1_dim: list, node2_dim: list, node3_dim: list, node4_dim: list, comp_id: int = 0):
        node1_id, node1_x, node1_y = self.add_node(*node1_dim)
        node2_id, node2_x, node2_y = self.add_node(*node2_dim)
        node3_id, node3_x, node3_y = self.add_node(*node3_dim)
        node4_id, node4_x, node4_y = self.add_node(*node4_dim)

        element_id = len(self.element_2D)
        new_element = np.array([[element_id, comp_id, 0,
                                node1_x, node1_y,
                                node2_x, node2_y,
                                node3_x, node3_y,
                                node4_x, node4_y]], dtype=np.float32)  # shape (1, 10)

        self.element_2D = np.vstack([self.element_2D, new_element])

        new_element_to_nodes = np.array([[node1_id, node2_id, node3_id, node4_id]], dtype=np.int32)  # shape (1, 4)
        self.element_to_nodes = np.vstack([self.element_to_nodes, new_element_to_nodes])
        
        return element_id

    def organize(self, area: dict):
        # AND each "range" constraint (element must satisfy all range boxes)
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
        on_drag = math.ceil(distance/element_size)
        if f_ne(on_drag, distance/element_size):
            element_size = distance / on_drag
            
        exist_element_2D = self.element_2D[self.element_2D[:, ELEMENT_COMP_ID] != 0]
        
        ### drag first to end-1
        for i in range(on_drag):
            ### record z info
            if i == on_drag - 1:
                self.z_table.append(end)
            else:
                z_now += element_size
                self.z_table.append(z_now)
            
            ### add the element
            if len(exist_element_2D) > 0:
                self.element_3D.append(exist_element_2D[:,[ELEMENT_ID, ELEMENT_COMP_ID]].astype(np.int32))
            else:
                self.element_3D.append([])
        
    ### wrap operation
    def build_block(self, element_size: float, x_list: list, y_list):
        new_x_list = [x_list[0]]
        new_y_list = [y_list[0]]
        
        ### calculate the reference point
        for i in range(1, len(x_list)):
            taget_num = math.ceil((x_list[i] - x_list[i-1]) / element_size)
            unit_len = (x_list[i] - x_list[i-1]) / taget_num
            now = x_list[i-1] + unit_len
            for _ in range(taget_num-1):
                new_x_list.append(now)
                now += unit_len
            new_x_list.append(x_list[i])
        for i in range(1, len(y_list)):
            taget_num = math.ceil((y_list[i] - y_list[i-1]) / element_size)
            unit_len = (y_list[i] - y_list[i-1]) / taget_num
            now = y_list[i-1] + unit_len
            for _ in range(taget_num-1):
                new_y_list.append(now)
                now += unit_len
            new_y_list.append(y_list[i])
            
        ### begin to build the checkerboard
        for i in range(1, len(new_x_list)):
            x_pre = new_x_list[i-1]
            x_post = new_x_list[i]
            for j in range(1, len(new_y_list)):
                y_pre = new_y_list[j-1]
                y_post = new_y_list[j]
                #print([x_pre, y_pre], [x_pre, y_post], [x_post, y_post], [x_post, y_pre])
                self.add_element([x_pre, y_pre], [x_pre, y_post], [x_post, y_post], [x_post, y_pre])      
    
    def build_blocks(self, element_size: float, section_type: list, table_x_dim: list, table_y_dim: list):
        ceil_table = [10000000 for _ in section_type]
        reference_node = [False for _ in table_x_dim]
        record_visit = [[False] * len(row) for row in section_type]
        
        section_num_x = len(table_x_dim)-1
        section_num_y = len(table_y_dim)-1
        
        for j in range(0, section_num_y):
            for i in range(0, section_num_x):
                if section_type[i][j] == 2 and not record_visit[i][j]:
                    ### find the rightest
                    right = i + 1
                    while right < section_num_x and section_type[right][j] == 2:
                        right += 1

                    ### find the ceil of each section (only execute while begin at y)
                    upper = 10000000
                    for m in range(i, right):
                        if j == 0 or section_type[m][j-1] != 2:
                            ### find the ceil
                            n = j + 1
                            while n < section_num_y and section_type[m][n] == 2:
                                n += 1
                            ceil_table[m] = n
                            
                        ### find the lowest ceil
                        upper = min(upper, ceil_table[m])
                        
                    ### left wall
                    if i > 1 and section_type[i-1][j] != 2:
                        n = j + 1
                        while n < section_num_y and section_type[i][n] != 2:
                            n += 1
                        upper = min(upper, n)
                    
                    ### right wall
                    if right != len(section_type) and section_type[right][j] != 2:
                        n = j + 1
                        while n < section_num_y and section_type[right][n] != 2:
                            n += 1
                        upper = min(upper, n)
                    
                    ### determine the reference element
                    for m in range(i+1, right-1):
                        ### clear the reference mark 
                        if section_type[m][j-1] != 2:
                            if section_type[m-1][j-1] != 2:
                                #reference_node[m] = False
                                print("~")
                            if section_type[m+1][j-1] != 2:
                                #reference_node[m+1] = False
                                print("~")
                        
                        ### set the reference node
                        if ceil_table[m] != ceil_table[m-1]:
                            reference_node[m] = True
                        if ceil_table[m] != ceil_table[m+1]:
                            reference_node[m+1] = True
                            
                        ### find the lowest ceil
                        upper = min(upper, ceil_table[m])
                        
                        ### update the reference mark
                        if m > i and ceil_table[m-1] != ceil_table[m]:
                            reference_node[m] = True
                            
                    reference_node[i] = True
                    reference_node[right] = True

                    ### set the visited section to true     
                    for m in range(i, right):
                        for n in range(j, upper):
                            record_visit[m][n] = True

                    ### build the x_list & y_list
                    y_list = [table_y_dim[j], table_y_dim[upper]]
                    x_list = []
                    for m in range(i, right+1):
                        if reference_node[m]:
                            x_list.append(table_x_dim[m])

                    ### build the block 
                    self.build_block(element_size, x_list, y_list)
                    print(f"{i} - {right}")
                    print(f"{j} - {upper}")
                    print(reference_node)
                    print(ceil_table)
                    print(x_list)
                    print("")

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
        ### if z out of the range z, return []
        if f_lt(node3_z, self.z_table[0], tolerance):
            return []
        if f_lt(self.z_table[-1], node1_z, tolerance):
            return []
        
        bottom_index = 0
        while f_lt(self.z_table[bottom_index], node1_z, tolerance):
            bottom_index += 1
        top_index = len(self.z_table) - 1
        while f_lt(node3_z, self.z_table[top_index], tolerance):
            top_index -= 1
        
    ### CDB format
    def read_CDB(self):
        print("~")
        
    def generate_cdb(self, path: str = 'cdb.txt', element_type: str = "185"):
        ### due to the "EMPTY"(0) type, there are nodes and elements not exist. so we need the table to record the offset
        node_offset = np.zeros(self.nodes.shape, dtype=np.int32)
        np.zeros(self.element_2D.shape, dtype=np.int32)
        
        with open(path, 'w') as f:
            ### build the nodes
            node_id_offset = 1
            node_id_icr = len(self.nodes)
            f.write(f"nodes:\n")
            
            ### the other layer
            for z in self.z_table:
                for index, node in enumerate(self.nodes):
                    f.write(f"    {index + node_id_offset}. {node[0]} {node[1]} {z}\n")
                node_id_offset += node_id_icr
                 
            ### build the elements
            node_id_offset = 1
            node_id_icr = len(self.nodes)
            element_id_offset = 1
            f.write(f"element:\n")
            for elements in self.element_3D:
                for index, element in enumerate(elements):
                    id = index + element_id_offset
                    nodes = self.element_to_nodes[element[0]]
                    node1 = nodes[0] + node_id_offset
                    node2 = nodes[1] + node_id_offset
                    node3 = nodes[2] + node_id_offset
                    node4 = nodes[3] + node_id_offset
                    node5 = nodes[0] + node_id_offset + node_id_icr
                    node6 = nodes[1] + node_id_offset + node_id_icr
                    node7 = nodes[2] + node_id_offset + node_id_icr
                    node8 = nodes[3] + node_id_offset + node_id_icr
                    f.write(f"      {id}. {node1} {node2} {node3} {node4} {node5} {node6} {node7} {node8}\n")
                element_id_offset += len(elements)
                node_id_offset += node_id_icr
                
            ### build the component
            line_now = 0
            for material, comp_id in self.material_table.items():
                if comp_id != 0:
                    f.write(f"COMP-{material}:")
                    
                    element_id_offset = 1
                    element_id_icr = len(self.element_2D)
                    for elements in self.element_3D:
                        indices = np.where(elements[:,1] == comp_id)[0]
                        for index in indices:
                            if line_now == 0:
                                f.write(f"\n    ")
                            line_now = (line_now + 1) % CDB_COMP_ELEM_PER_LINE
                                
                            f.write(f"{index + element_id_offset} ")
                        element_id_offset += element_id_icr
                    f.write(f"\n")
            
    ### Debug
    def show_2d_graph(self, title: str = "2D mesh"):
        material_to_color = {
            index: cm.tab20(index / max(1, len(self.material_table) - 1)) for material, index in self.material_table.items()
        }
        for element in self.element_2D:
            x_coords = [
                element[ELEMENT_NODE1_X],
                element[ELEMENT_NODE2_X],
                element[ELEMENT_NODE3_X],
                element[ELEMENT_NODE4_X]
            ]
            y_coords = [
                element[ELEMENT_NODE1_Y],
                element[ELEMENT_NODE2_Y],
                element[ELEMENT_NODE3_Y],
                element[ELEMENT_NODE4_Y]
            ]
            color = material_to_color[element[ELEMENT_COMP_ID]]
            
            plt.fill(x_coords, y_coords, color=color, edgecolor='black')

        plt.gca().set_aspect('equal')
        plt.grid(True)
        plt.title(f"{title}")
        plt.show()
        plt.close()
        
    def show_info(self):
        total_num = len(self.element_2D)
        
        ### basic info
        print(f"[Basic Info]:")
        print(f"    total num: {total_num}")
        
        ### comp info
        print(f"[COMP info]:")
        for material, comp_id in self.material_table.items():
            elements = self.element_2D[self.element_2D[:, ELEMENT_COMP_ID] == comp_id]
            print(f"    {material}: {len(elements)} items")