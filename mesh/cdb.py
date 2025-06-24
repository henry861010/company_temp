import numpy as np
import math
import matplotlib.pyplot as plt
#from my_math import *

'''
    elements: [
        {
            element_id,
            comp_id,
            node1_x, node1_y,
            node2_x, node2_y,
            node3_x, node3_y,
            node4_x, node4_y
        }
    ]
    element_nodes: [
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
    
    area: {
        comp_id
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
ELEMENT_NODE1_X = 2
ELEMENT_NODE1_Y = 3
ELEMENT_NODE2_X = 4
ELEMENT_NODE2_Y = 5
ELEMENT_NODE3_X = 6
ELEMENT_NODE3_Y = 7
ELEMENT_NODE4_X = 8
ELEMENT_NODE4_Y = 9

ELEMENT_COMP_ID = 0

class CDB:
    def __init__(self):
        self.components = [] ### [component_name, ... ]
        self.elements = np.empty((0, 10), dtype=np.float32)
        self.element_nodes = np.empty((0, 4), dtype=np.float32)
        self.nodes = np.empty((0, 2), dtype=np.float32)
        self.materials = []
        self.node_map = {}
        
        ### implicit info
        self._node_num = 0
        self._element_num = 0
        self.z_offset = 0

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

        element_id = len(self.elements)
        new_element = np.array([[element_id, comp_id,
                                node1_x, node1_y,
                                node2_x, node2_y,
                                node3_x, node3_y,
                                node4_x, node4_y]], dtype=np.float32)  # shape (1, 10)

        self.elements = np.vstack([self.elements, new_element])

        new_element_nodes = np.array([[node1_id, node2_id, node3_id, node4_id]], dtype=np.float32)  # shape (1, 4)
        self.element_nodes = np.vstack([self.element_nodes, new_element_nodes])

        self._element_num += 1
        return element_id
    
    def show_graph(self, title: str = "2D mesh"):
        ### show the element
        for element in self.elements:
            plt.plot([element[ELEMENT_NODE1_X], element[ELEMENT_NODE2_X]], [element[ELEMENT_NODE1_Y], element[ELEMENT_NODE2_Y]], color='black')
            plt.plot([element[ELEMENT_NODE2_X], element[ELEMENT_NODE3_X]], [element[ELEMENT_NODE2_Y], element[ELEMENT_NODE3_Y]], color='black')
            plt.plot([element[ELEMENT_NODE3_X], element[ELEMENT_NODE4_X]], [element[ELEMENT_NODE3_Y], element[ELEMENT_NODE4_Y]], color='black')
            plt.plot([element[ELEMENT_NODE4_X], element[ELEMENT_NODE1_X]], [element[ELEMENT_NODE4_Y], element[ELEMENT_NODE1_Y]], color='black')
            
        plt.gca().set_aspect('equal')
        plt.grid(True)
        plt.title(f"{title}")
        plt.show()
        plt.close()
    
    def generate_cdb(self):
        with open('cdb.txt', 'w') as f:
            f.write(f"nodes:\n")
            for index, node in enumerate(self.nodes):
                 f.write(f"    {index}. {node[0]} {node[1]}\n")
            f.write(f"element:\n")
            for index, element in enumerate(self.elements):
                 f.write(f"    {index}. {element[0]} {element[1]} {element[2]} {element[3]} {element[4]}\n")
    
    def cal_areas(self):
        # Extract coordinates as (N, 4) for each x and y
        x1, y1 = self.elements[:, ELEMENT_NODE1_X],  self.elements[:, ELEMENT_NODE1_X]
        x2, y2 = self.elements[:, ELEMENT_NODE2_X],  self.elements[:, ELEMENT_NODE2_X]
        x3, y3 = self.elements[:, ELEMENT_NODE3_X],  self.elements[:, ELEMENT_NODE3_X]
        x4, y4 = self.elements[:, ELEMENT_NODE4_X],  self.elements[:, ELEMENT_NODE4_X]

        # Shoelace formula for quadrilateral
        areas = 0.5 * np.abs(
            x1*y2 + x2*y3 + x3*y4 + x4*y1 -
            (y1*x2 + y2*x3 + y3*x4 + y4*x1)
        )

        # Store back into column 13
        self.elements[:, ELEMENT_AREA] = areas
    
    def organize(self, area: dict):
        # Start with all True (include everything initially)
        mask = np.ones(len(self.elements), dtype=bool)

        # AND each range box constraint (element must satisfy all range boxes)
        range_masks = []
        for range_info in area["ranges"]:
            if range_info["type"] == "BOX":
                range_info.append(
                    (self.elements[:, ELEMENT_NODE1_X] >= range_info["dim"][0]) &
                    (self.elements[:, ELEMENT_NODE1_Y] >= range_info["dim"][1]) &
                    (self.elements[:, ELEMENT_NODE3_X] <= range_info["dim"][2]) &  # corrected
                    (self.elements[:, ELEMENT_NODE3_Y] <= range_info["dim"][3])    # corrected
                )
        if len(range_masks) > 0:
            target_elements = self.elements[np.logical_or.reduce(range_masks)]

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
                comp_id = self.materials[metal_info["material"]]
                exclude_masks.append(
                    ~(target_elements[:, ELEMENT_COMP_ID] == comp_id)
                )
        if len(exclude_masks) > 0:
            target_elements = target_elements[np.logical_and.reduce(exclude_masks)]
        
        ### assign the metal "NORMAL"
        np.random.shuffle(target_elements)
        index = len(target_elements) - 1
        for metal_info in area["metals"]:
            if metal_info["type"] == "NORMAL":
                comp_id = self.materials[metal_info["material"]]
                seleted_area = 0
                while seleted_area < total_area and index >= 0:
                    seleted_area += target_elements[index][ELEMENT_AREA]
                    target_elements[index][ELEMENT_COMP_ID] = comp_id
                    index -= 1
        target_elements = target_elements[0 : index + 1]
                    
        ### assign the material
        target_element_index = target_elements[:, ELEMENT_ID].astype(int)
        self.elements[target_element_index, ELEMENT_COMP_ID] = self.materials[area["material"]]
        
    def drag(self, end: float, element_size: float):
        print("")
        
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
                    
                    ### determine the reference node
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

section_typ = [
    [0, 2, 2, 2, 2, 2, 0, 0, 0, 0],
    [0, 2, 2, 2, 2, 2, 0, 0, 0, 0],
    [0, 0, 0, 2, 2, 2, 0, 2, 0, 0],
    [0, 0, 0, 2, 2, 2, 0, 2, 2, 2],
    [0, 2, 2, 2, 2, 2, 0, 2, 2, 2],
    [0, 2, 2, 2, 2, 2, 0, 2, 0, 0],
    [0, 0, 0, 0, 2, 2, 2, 2, 2, 2],
    [0, 0, 0, 0, 2, 2, 0, 2, 2, 2],
    [0, 0, 0, 0, 2, 2, 0, 2, 2, 2],
    [0, 0, 0, 0, 2, 2, 0, 0, 0, 0]
]
table_x_dim = [0, 10, 23, 37, 41, 53, 69, 76, 85, 91, 104]
table_y_dim = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

cdb = CDB()
cdb.build_blocks(4, section_typ, table_y_dim, table_y_dim)
cdb.show_graph()