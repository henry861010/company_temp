import numpy as np
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
        self.elements = np.empty((0, 15), dtype=np.float32)
        self.nodes = np.empty((0, 2), dtype=np.float32)
        self.materials = []
        self.node_map = {}
        
        ### implicit info
        self._node_num = 0
        self._element_num = 0
        self.z_offset = 0

    def add_node(self, x: float, y: float):
        node_key = f"{x}-{y}"
        if not node_key in self.node_map:
            self.nodes.append(np.array([x, y], dtype=np.float32))
            node_id = len(self.nodes) - 1
            self.node_map[node_key] = node_id
        return (node_id, x, y)

    def add_element(self, node1_dim: list, node2_dim: list, node3_dim: list, node4_dim: list, comp_id: int):
        node1_id, node1_x, node1_y  = self.add_node(node1_dim[0], node1_dim[1])
        node2_id, node2_x, node2_y = self.add_node(node2_dim[0], node2_dim[1])
        node3_id, node3_x, node3_y = self.add_node(node3_dim[0], node3_dim[1])
        node4_id, node4_x, node4_y = self.add_node(node4_dim[0], node4_dim[1])
        np.append(self.elements, np.array([len(self.elements), comp_id, node1_x, node1_y, node2_x, node2_y, node3_x, node3_y, node4_x, node4_y], dtype=np.float32))
        np.append(self.element_nodes, np.array([node1_id, node2_id, node3_id, node4_id], dtype=np.float32))
        self._element_num += 1
        return len(self.elements) - 1
    
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
                self.add_element([x_pre, y_pre], [x_pre, y_post], [x_post, y_post], [x_post, y_pre])      
    
    def show_graph(self, title: str = "2D mesh"):
        ### show the element
        for element in self.elements:
            plt.plot([self.elements[ELEMENT_NODE1_X], self.elements[ELEMENT_NODE2_X]], [self.elements[ELEMENT_NODE1_Y], self.elements[ELEMENT_NODE2_Y]], color='black')
            plt.plot([self.elements[ELEMENT_NODE2_X], self.elements[ELEMENT_NODE3_X]], [self.elements[ELEMENT_NODE2_Y], self.elements[ELEMENT_NODE3_Y]], color='black')
            plt.plot([self.elements[ELEMENT_NODE3_X], self.elements[ELEMENT_NODE4_X]], [self.elements[ELEMENT_NODE3_Y], self.elements[ELEMENT_NODE4_Y]], color='black')
            plt.plot([self.elements[ELEMENT_NODE4_X], self.elements[ELEMENT_NODE1_X]], [self.elements[ELEMENT_NODE4_Y], self.elements[ELEMENT_NODE1_Y]], color='black')
            
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
        np.append(self.all, self.elements[:, ELEMENT_COMP_ID])