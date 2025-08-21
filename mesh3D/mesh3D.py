ELEMENT_LEN = 8
NODE_LEN = 3

ELEMENT_2D_LEN = 11
ELEMENT_2D_ID = 0
ELEMENT_2D_COMP_ID = 1
ELEMENT_2D_AREA = 2
ELEMENT_2D_NODE1_X = 3
ELEMENT_2D_NODE1_Y = 4
ELEMENT_2D_NODE2_X = 5
ELEMENT_2D_NODE2_Y = 6
ELEMENT_2D_NODE3_X = 7
ELEMENT_2D_NODE3_Y = 8
ELEMENT_2D_NODE4_X = 9
ELEMENT_2D_NODE4_Y = 10

class Mesh3D:
    def __init__(self):
        self.elements = np.empty((0, ELEMENT_LEN), dtype=np.int32)
        self._2Ds = np.empty((0), dtype=np.int32)
        self.element_comps = np.empty((0), dtype=np.int32)
        self.nodes = np.empty((0, NODE_LEN), dtype=np.float64)
        self.ids = np.empty((0), dtype=np.int32)
        self.comps = {}
        
        ### process
        self.element_2D = np.empty((0, ELEMENT_2D_LEN), dtype=np.float32)
        self.element_2D_nodes = np.empty((0, 4), dtype=np.int32)
        self.node_2D = np.empty((0, 2), dtype=np.float32)
        
    def cal_areas(self):
        # Extract coordinates as (N, 4) for each x and y
        x1, y1 = self.element_2D[:, ELEMENT_2D_NODE1_X],  self.element_2D[:, ELEMENT_2D_NODE1_Y]
        x2, y2 = self.element_2D[:, ELEMENT_2D_NODE2_X],  self.element_2D[:, ELEMENT_2D_NODE2_Y]
        x3, y3 = self.element_2D[:, ELEMENT_2D_NODE3_X],  self.element_2D[:, ELEMENT_2D_NODE3_Y]
        x4, y4 = self.element_2D[:, ELEMENT_2D_NODE4_X],  self.element_2D[:, ELEMENT_2D_NODE4_Y]

        # Shoelace formula for quadrilateral
        areas = 0.5 * np.abs(
            x1*y2 + x2*y3 + x3*y4 + x4*y1 -
            (y1*x2 + y2*x3 + y3*x4 + y4*x1)
        )

        # Store back into column 13
        self.element_2D[:, ELEMENT_2D_AREA] = areas
    
    def search(self, elements, type, dim):
        x_coords = elements[:, [ELEMENT_2D_NODE1_X, ELEMENT_2D_NODE2_X, ELEMENT_2D_NODE3_X, ELEMENT_2D_NODE4_X]]
        y_coords = elements[:, [ELEMENT_2D_NODE1_Y, ELEMENT_2D_NODE2_Y, ELEMENT_2D_NODE3_Y, ELEMENT_2D_NODE4_Y]]

        if type == "BOX":
            bl_x, bl_y, tr_x, tr_y = dim[0], dim[1], dim[2], dim[3]
            mask = (x_coords >= bl_x) & (x_coords <= tr_x) & (y_coords >= bl_y) & (y_coords <= tr_y)
            mask = np.all(mask, axis=1)

        elif type == "CYLINDER":
            center_x, center_y, radius = dim[0], dim[1], dim[2]
            dist_sq = (x_coords - center_x)**2 + (y_coords - center_y)**2
            mask = np.all(dist_sq <= radius**2, axis=1)

        else:
            raise ValueError(f"Unsupported type: {type}")

        return mask
    
    def assign_metal(self, elements, metal, total_area):
        ### the assigned material
        if not metal_info["material"] in self.comps:
            new_comp_id = len(self.comps)
            self.comps[metal_info["material"]] = new_comp_id
        comp_id = self.comps[metal_info["material"]]
                
        ### Include    
        if "ranges" in metal and metal["ranges"]:
            mask = np.logical_or.reduce([search(self, elements, r["type"], r["dim"]) for r in metal["ranges"]])
        else:
            mask = np.ones(len(elements), dtype=bool)

        ### Exclude
        if "holes" in metal and metal["holes"]:
            mask &= np.logical_and.reduce([~search(self, elements, h["type"], h["dim"]) for h in metal["holes"]])

        target_elements = elements[mask]

        ### begin to assign the metal
        seleted_area = 0
        index = len(target_elements) - 1
        while index >= 0 and (seleted_area / total_area) < metal_info["density"]/100:
            seleted_area += target_elements[index][ELEMENT_2D_AREA]
            element_id = int(target_elements[index][ELEMENT_2D_ID])
            self.element_2D[element_id][ELEMENT_2D_COMP_ID] = comp_id
            index -= 1     
            
        ### remaining id
        return target_elements[:index+1][ELEMENT_2D_ID]
        
    def organize(self, area: dict):
        # AND each "range" constraint (element must satisfy all range boxes)
        if "ranges" in area and area["ranges"]:
            mask = np.zeros(len(self.element_2D), dtype=bool)
            for range_info in area["ranges"]:
                mask |= search(self, self.element_2D, range_info["type"], range_info["dim"])
        else:
            mask = np.ones(len(self.element_2D), dtype=bool)
        target_elements = self.element_2D[mask]

        # Exclude any that intersect with a hole
        if "holes" in area
            for hole_info in area["holes"]:
                mask = search(self, target_elements, hole_info["type"], hole_info["dim"])
                target_elements = target_elements[~mask]
        
        ### calculate the area
        total_area = target_elements[:, ELEMENT_2D_AREA].sum()
        
        ### assign the metal "CONTINUE"
        mask = np.zeros(len(target_elements), dtype=bool)
        for metal_info in area["metals"]:
            if metal_info["type"] == "CONTINUE":
                comp_id = self.comps[metal_info["material"]]
                mask &= (target_elements[:, ELEMENT_2D_COMP_ID] == comp_id)
        target_elements = target_elements[~mask]
        
        ### assign the metal "NORMAL"
        ### NOTE: np.random.shuffle is very slow!!!
        if len(area["metals"]) > 0:
            np.random.seed(1)
            np.random.shuffle(target_elements)
            for metal_info in area["metals"]:
                if metal_info["type"] == "NORMAL":
                    remaining_ids = self.assign_metal(target_elements, metal_info, total_area)
                    target_elements = target_elements[remaining_ids]
                    
        ### assign the material
        if not area["material"] in self.comps:
            new_comp_id = len(self.comps)
            self.comps[area["material"]] = new_comp_id
        target_element_index = target_elements[:, ELEMENT_2D_ID].astype(int)
        self.element_2D[target_element_index, ELEMENT_2D_COMP_ID] = self.comps[area["material"]]
        
    def drag(self, element_size: float, end: float):
        z_now = self.z_table[-1]
        distance = round(end - z_now, 5)
        
        # Adjust element size if not evenly divisible
        on_drag = math.ceil(distance / element_size)
        if abs(on_drag -  distance/element_size) > 0.00001:
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