import numpy as np
import time
from matplotlib.patches import Polygon
from matplotlib.path import Path

ELEMENT_LEN = 8
NODE_LEN = 3

ELEMENT_2D_LEN = 10
ELEMENT_2D_COMP_ID = 0
ELEMENT_2D_VOLUMN = 1
ELEMENT_2D_NODE1_X = 2
ELEMENT_2D_NODE1_Y = 3
ELEMENT_2D_NODE2_X = 4
ELEMENT_2D_NODE2_Y = 5
ELEMENT_2D_NODE3_X = 6
ELEMENT_2D_NODE3_Y = 7
ELEMENT_2D_NODE4_X = 8
ELEMENT_2D_NODE4_Y = 9

class Mesh3D:
    def __init__(self):
        ### component
        self.comps = {"EMPTY":0}
        
        ### 3D elements
        self.element_num = 0
        self.elements = np.empty((0, ELEMENT_LEN), dtype=np.int32)
        self.element_ids = np.empty((0), dtype=np.int32)
        self.element_comps = np.empty((0), dtype=np.int32)
        
        ### nodes
        self.node_num = 0
        self.nodes = np.empty((0, NODE_LEN), dtype=np.float32)
        self.node_ids = np.empty((0), dtype=np.float32)
        
        ### process
        self.element_2D = np.empty((0, ELEMENT_2D_LEN), dtype=np.float32)
        self.element_2D_nodes = np.zeros((0, 4), dtype=np.int32)
        
        self.node_2D = np.empty((0, 2), dtype=np.float32)
        self.node_2D_to_3D = np.zeros((0), dtype=np.int32)
        
    ### initial
    def initial(self, parser:'Mesh2D'):
        element_coords, element_node_ids, node_coords, node_ids = parser.get()
        self.element_2D = np.empty((len(element_coords), ELEMENT_2D_LEN), dtype=np.float32)
        
        self.element_2D[:,ELEMENT_2D_NODE1_X:ELEMENT_2D_NODE4_Y+1] = element_coords.reshape(element_coords.shape[0], 8)
        self.element_2D[:,ELEMENT_2D_COMP_ID] = 0
        self.element_2D_nodes = element_node_ids
        
        self.node_2D = node_coords
        self.node_2D_to_3D = np.zeros(len(node_coords), dtype=np.int32) - 1
        
        self.cal_volumns()
        
    def set_2D(self, mesh2D):
        self.element_2D_nodes = mesh2D.get_elements()
        self.node_2D = mesh2D.get_nodes()
        
        self.element_2D = np.empty((self.element_2D_nodes.size, ELEMENT_2D_LEN), dtype=np.float32)
        self.element_2D[:,ELEMENT_2D_NODE1_X:ELEMENT_2D_NODE4_Y+1] = element_coords.reshape(element_coords.shape[0], 8)
        self.element_2D[:,ELEMENT_2D_COMP_ID] = 0
        
        self.node_2D_to_3D = np.zeros(len(node_coords), dtype=np.int32) - 1
        
        self.cal_volumns()
    
    ### foundmental
    def _pre_allocate_nodes(self, size: int = 1):
        required = self.node_num + size
        current_capacity = len(self.nodes)
        if required > current_capacity:
            new_capacity = max(required, int(current_capacity * 1.5))
            extra = new_capacity - current_capacity
            
            self.nodes = np.vstack([self.nodes, np.empty((extra, 3), dtype=np.float32)])
            self.node_ids = np.concatenate([self.node_ids, np.empty(extra, dtype=np.int32)])

    def _pre_allocate_elements(self, size: int = 1):
        required = self.element_num + size
        current_capacity = len(self.elements)
        if required > current_capacity:
            new_capacity = max(required, int(current_capacity * 1.5))
            extra = new_capacity - current_capacity
            
            self.elements = np.vstack([self.elements, np.empty((extra, 8), dtype=np.int32)])
            self.element_ids = np.concatenate([self.element_ids, np.empty(extra, dtype=np.int32)])
            self.element_comps = np.concatenate([self.element_comps, np.empty(extra, dtype=np.int32)])
        
    ### function
    def cal_volumns(self):
        # Extract coordinates as (N, 4) for each x and y
        x1, y1 = self.element_2D[:, ELEMENT_2D_NODE1_X],  self.element_2D[:, ELEMENT_2D_NODE1_Y]
        x2, y2 = self.element_2D[:, ELEMENT_2D_NODE2_X],  self.element_2D[:, ELEMENT_2D_NODE2_Y]
        x3, y3 = self.element_2D[:, ELEMENT_2D_NODE3_X],  self.element_2D[:, ELEMENT_2D_NODE3_Y]
        x4, y4 = self.element_2D[:, ELEMENT_2D_NODE4_X],  self.element_2D[:, ELEMENT_2D_NODE4_Y]

        # Shoelace formula for quadrilateral
        voulmn = 0.5 * np.abs(
            x1*y2 + x2*y3 + x3*y4 + x4*y1 -
            (y1*x2 + y2*x3 + y3*x4 + y4*x1)
        )

        # Store back into column 13
        self.element_2D[:, ELEMENT_2D_VOLUMN] = voulmn
        
    def search_face(self, elements, type, dim, index=None, eps=0.0):
        """
            Fast predicate on subset indices (index). 
            Returns a boolean mask aligned to index (or to all rows if index is None).
        """
        rows = index if index is not None else slice(None)
        
        # gather 4 corners
        cols = np.array([ELEMENT_2D_NODE1_X, ELEMENT_2D_NODE2_X, ELEMENT_2D_NODE3_X, ELEMENT_2D_NODE4_X], dtype=int)
        x4 = elements[np.ix_(rows, cols)]
        cols = np.array([ELEMENT_2D_NODE1_Y, ELEMENT_2D_NODE2_Y, ELEMENT_2D_NODE3_Y, ELEMENT_2D_NODE4_Y], dtype=int)
        y4 = elements[np.ix_(rows, cols)]
        
        ### max/min of each elements
        min_x = x4.min(axis=1)
        max_x = x4.max(axis=1)
        min_y = y4.min(axis=1)
        max_y = y4.max(axis=1)

        if type == "BOX":
            bl_x, bl_y, tr_x, tr_y = dim
            if eps:
                bl_x -= eps
                bl_y -= eps
                tr_x += eps
                tr_y += eps
            return (min_x >= bl_x) & (max_x <= tr_x) & (min_y >= bl_y) & (max_y <= tr_y)

        elif type == "CYLINDER":
            cx, cy, r = dim
            rr = r*r + 0.0
            if eps:
                rr = (r + eps) * (r + eps)
            dist = (x4 - cx)**2 + (y4 - cy)**2
            return np.all(dist <= rr, axis=1)
        
        elif type == "POLYGON":
            radiu = -1e-12
            path = Path(np.asarray(dim, float))
            
            node1_list = self.element_2D[:, [ELEMENT_2D_NODE1_X,ELEMENT_2D_NODE1_Y]]
            mask1 = path.contains_points(node1_list, radius=radiu)

            node2_list = self.element_2D[:, [ELEMENT_2D_NODE2_X,ELEMENT_2D_NODE2_Y]]
            mask2 = path.contains_points(node2_list, radius=radiu)
            
            node3_list = self.element_2D[:, [ELEMENT_2D_NODE3_X,ELEMENT_2D_NODE3_Y]]
            mask3 = path.contains_points(node3_list, radius=radiu)
            
            node4_list = self.element_2D[:, [ELEMENT_2D_NODE4_X,ELEMENT_2D_NODE4_Y]]
            mask4 = path.contains_points(node4_list, radius=radiu)
            return mask1 & mask2 & mask3 & mask4
        else:
            raise ValueError(f"Unsupported type: {type}")

    def search_faces(self, elements, ranges=None, holes=None, returnMask=False):
        """
        Ranges-first progressive search using only index arrays (no big copies).
        Returns a index over 'elements'.
        """
        n = len(elements)
        if n == 0:
            if returnMask:
                return np.zeros(0, dtype=bool)
            else:
                return np.zeros(0, dtype=np.int32)

        included_mask = np.zeros(n, dtype=bool)

        ### Include
        if ranges:
            canidate_indices = np.arange(n, dtype=np.int32)
            for r in ranges:
                if len(canidate_indices) == 0:
                    break
                submask = self.search_face(elements, r["type"], r["dim"], index=canidate_indices)
                if np.any(submask):
                    hit_indices = canidate_indices[submask]
                    included_mask[hit_indices] = True
                    canidate_indices = canidate_indices[~submask]  # short-circuit: drop already-included_mask
        else:
            included_mask[:] = True

        ### Exclude
        if holes:
            live_indices = np.nonzero(included_mask)[0]
            for h in holes:
                if len(live_indices) == 0:
                    break
                submask = self.search_face(elements, h["type"], h["dim"], index=live_indices)
                if np.any(submask):
                    lose_indices = live_indices[submask]
                    included_mask[lose_indices] = False
                    live_indices = live_indices[~submask]
        if returnMask:
            return included_mask
        else:
            return np.flatnonzero(included_mask) 

    def assign_metal(self, elements, density, total_volume, isRandomSeed=False):
        """
        Randomly pick elements (from 'elements' rows) until reaching density% of total_volume.
        Operates by shuffling indices only and using cumsum to avoid Python loops.
        Returns the remaining *row indices within this subset* (not global IDs).
        """
        target_indices = np.arange(len(elements), dtype=np.int32)
        
        # target volume
        target = (density / 100.0) * total_volume
        vols = elements[:, ELEMENT_2D_VOLUMN]

        # random order of candidates (indices only, not rows)
        rng = np.random.default_rng(None if isRandomSeed else 1)
        random_indices = target_indices[rng.permutation(len(elements))]

        # cumulative sum until target
        csum = np.cumsum(vols[random_indices])
        k = np.searchsorted(csum, target, side="right")  # number to take (may be 0)
        if k > 0:
            chosen_indices  = target_indices[random_indices[:k]]
            return chosen_indices
        else:
            # no assignment if density threshold is 0 or vols too small
            return np.empty((0), dtype=np.int32), np.arange(len(elements))

    def organize(self, areas):
        if isinstance(areas, dict):
            areas = [areas]
            
        for area in areas:
            ### Select the area once (mask -> indices)
            ranges = [{"type": area["type"], "dim": area["dim"]}]
            holes  = area.get("holes")
            area_indices  = self.search_faces(self.element_2D, ranges, holes)  # boolean over elements
            if len(area_indices) == 0:
                return

            ### Working pool: local indices into area_idx
            remaining_indices = np.arange(len(area_indices), dtype=np.int32)

            ### Convenience views for writes/reads via global IDs
            area_comps = self.element_2D[area_indices, ELEMENT_2D_COMP_ID]

            ### Volumes for NORMAL metals (within area)
            for metal in area.get("metals", []):
                if metal["type"] == "NORMAL":
                    ranges = metal.get("ranges")
                    holes = metal.get("holes")
                    metal_indices = self.search_faces(self.element_2D[area_indices], ranges, holes)
                    vol = self.element_2D[area_indices[metal_indices], ELEMENT_2D_VOLUMN].sum()
                    metal["volumn"] = float(vol)

            ### metal assignment CONTINUE
            for metal in area.get("metals", []):
                if metal["type"] == "CONTINUE":
                    ### find potential assignment area  
                    ranges = metal.get("ranges")
                    holes = metal.get("holes")
                    region_local = self.search_faces(self.element_2D[area_indices][remaining_indices], ranges, holes)  # indices in pool
                    remaining_target_indices = remaining_indices[region_local]
                
                    ### remove the assignment
                    if len(remaining_target_indices):
                        comp_id = self.comps[metal["material"]]
                        assigned_mask = (area_comps[remaining_target_indices] == comp_id)
                        if np.any(assigned_mask):
                            remaining_assigned_indices = remaining_target_indices[assigned_mask]
                            remaining_indices = np.setdiff1d(remaining_indices, remaining_assigned_indices, assume_unique=False)
            
            ### metal assignment CONVERT
            for metal in area.get("metals", []):
                if metal["type"] == "CONVERT":   
                    ### find potential assignment area  
                    ranges = metal.get("ranges")
                    holes = metal.get("holes")
                    region_local = self.search_faces(self.element_2D[area_indices][remaining_indices], ranges, holes)  # indices in pool
                    remaining_target_indices = remaining_indices[region_local]  
                                    
                    ### convert the assignment metal & remove the assignment
                    if len(remaining_target_indices):
                        material_old = metal["material_o"]
                        material_new = metal["material"]
                        if material_new not in self.comps: 
                            self.comps[material_new] = len(self.comps)
                        comp_id_old = self.comps[material_old] 
                        comp_id_new = self.comps[material_new]
                        
                        assigned_mask = (area_comps[remaining_target_indices] == comp_id_old)
                        if np.any(assigned_mask):
                            remaining_assigned_indices = remaining_target_indices[assigned_mask]
                            self.element_2D[area_indices[remaining_indices], ELEMENT_2D_COMP_ID] = comp_id_new
                            remaining_indices = np.setdiff1d(remaining_indices, remaining_assigned_indices, assume_unique=False)
            
            ### metal assignment Normal
            for metal in area.get("metals", []):
                if metal["type"] == "NORMAL": 
                    ### find potential assignment area  
                    ranges = metal.get("ranges")
                    holes = metal.get("holes")
                    density = metal.get("density")
                    volumn = metal.get("volumn")
                    
                    region_local = self.search_faces(self.element_2D[area_indices][remaining_indices], ranges, holes)  # indices in pool
                    remaining_target_indices = remaining_indices[region_local]  
                                                
                    ### assign metal
                    if len(remaining_target_indices):
                        ### find the assignment area
                        remaining_assigned_indices = self.assign_metal(self.element_2D[area_indices][remaining_target_indices], density, volumn)
                        assigned_indices  = remaining_target_indices[remaining_assigned_indices]
                        
                        ### assigne metal
                        material = metal["material"]
                        if material not in self.comps:
                            self.comps[material] = len(self.comps)
                        comp_id = self.comps[material]

                        ### assign the metal
                        self.element_2D[area_indices[assigned_indices], ELEMENT_2D_COMP_ID] = comp_id

                        ### remove assigned element
                        temp_mask = ~np.isin(remaining_indices, assigned_indices) 
                        remaining_indices = remaining_indices[temp_mask]

            ### assign the material
            if len(remaining_indices):
                material = area["material"]
                if material not in self.comps:
                    self.comps[material] = len(self.comps)
                comp_id = self.comps[material]
                self.element_2D[area_indices[remaining_indices], ELEMENT_2D_COMP_ID] = comp_id
        
    def organize_empty(self):
        self.element_2D[:,ELEMENT_2D_COMP_ID] = 0
        
    def drag(self, element_size: float, begin: float, end: float):
        ### calculate drag_num & element_size
        distance  = round(float(end) - float(begin), 5)
        if distance <= 0:
            return 0
        drag_num = int(np.ceil(distance / element_size))
        element_size = distance / drag_num

        ### target element index
        elem2D_idx = np.flatnonzero(self.element_2D[:, ELEMENT_2D_COMP_ID] != 0)
        if elem2D_idx.size == 0:
            return 0

        # unique 2D node ids used by those elements
        elem2D_nodes = self.element_2D_nodes[elem2D_idx]
        node2D_idx, inv = np.unique(elem2D_nodes, return_inverse=True)
        elem2D_nodes_local = inv.reshape(elem2D_nodes.shape)   

        ### add the unexisted node
        unexisted_node2D_idx = node2D_idx[self.node_2D_to_3D[node2D_idx] == -1]
        if unexisted_node2D_idx.size:
            self._pre_allocate_nodes(unexisted_node2D_idx.size)
            
            dst = self.nodes[self.node_num : self.node_num + unexisted_node2D_idx.size]
            np.take(self.node_2D, unexisted_node2D_idx, axis=0, out=dst[:, :2]) # xy from 2D nodes -> write directly without temp:
            dst[:, 2] = begin
            
            self.node_2D_to_3D[unexisted_node2D_idx] = np.arange(self.node_num, self.node_num + unexisted_node2D_idx.size, dtype=np.int32)
            self.node_num += unexisted_node2D_idx.size

        ### begin to drag
        base_map = self.node_2D_to_3D[node2D_idx]
        N = node2D_idx.size
        E = elem2D_idx.size

        ### [NODE] allocate all 3D nodes
        self._pre_allocate_nodes(N * drag_num)
        node_start = self.node_num
        new_node_ids = (node_start + np.arange(N * drag_num, dtype=np.int32)).reshape(drag_num, N)

        # fill XY for all layers (broadcast XY), and Z per layer
        xy = self.node_2D[node2D_idx]
        dst_nodes = self.nodes[node_start : node_start + N * drag_num]
        dst_nodes[:, :2] = np.broadcast_to(xy, (drag_num, N, 2)).reshape(N * drag_num, 2)

        z_vals = begin + element_size * (np.arange(1, drag_num + 1, dtype=dst_nodes.dtype))
        dst_nodes[:, 2] = np.repeat(z_vals, N)

        self.node_num += N * drag_num

        ### [ELEMENT] allocate all 3D elements
        self._pre_allocate_elements(E * drag_num)
        elem_start = self.element_num

        # layer->3D index table (drag_num+1, N): row0 = base, rows1..drag_num = new layers
        layer_nodes = np.empty((drag_num + 1, N), dtype=np.int32)
        layer_nodes[0]  = base_map
        layer_nodes[1:] = new_node_ids

        # For each layer k, bottom = layer_nodes[k-1][cols], top = layer_nodes[k][cols]
        # cols per element are the (E,4) indices into node2D_idx
        bottom = layer_nodes[:-1][:, elem2D_nodes_local]
        top    = layer_nodes[1:][:,  elem2D_nodes_local]
        elems  = np.concatenate([bottom, top], axis=2).reshape(drag_num * E, 8)

        ### assign nodes to each element
        self.elements[elem_start : elem_start + drag_num * E] = elems.astype(np.int32, copy=False)
        
        ### assign ids to each element
        self.element_ids[elem_start : elem_start + drag_num * E] = 1 + np.max(self.element_ids) + np.arange(drag_num * E)

        ### assign comps to each element
        layer_comps = self.element_2D[elem2D_idx, ELEMENT_2D_COMP_ID]
        dest = self.element_comps[elem_start : elem_start + drag_num * E].reshape(drag_num, E)
        dest[:] = layer_comps
        
        self.element_num += drag_num * E

        # update map so future ops start from the top layer
        self.node_2D_to_3D[:] = -1
        self.node_2D_to_3D[node2D_idx] = layer_nodes[-1]

    def engine(self, object_list):
        for obj in object_list:
            begin_z = obj["begin_z"]
            for layer in obj["layers"]:
                self.organize(layer["areas"])
                self.drag(layer["element_size"], begin_z, layer["z"])
                begin_z = layer["z"]
        self.equivalence()
        
    ### equivalence
    def equivalence(self, eps=1e-8):
        # Quantize (avoid float-equality issues)
        q = np.round(self.nodes / eps).astype(np.int32)

        # Unique on quantized rows
        _, inverse, keep_idx = np.unique(q, axis=0, return_inverse=True, return_index=True)

        # Remap element connectivity to canonical indices
        self.elements = inverse[self.elements]

        # Pick node IDs from the first occurrence (you can change policy if needed)
        self.node_ids = self.node_ids[keep_idx]

        self.nodes = self.nodes[keep_idx]

    ### result
    def get(self):
        elements = self.elements[:self.element_num]
        element_comps = self.element_comps[:self.element_num]
        nodes = self.nodes[:self.node_num]
        return elements, element_comps, nodes

    ### debug
    def show_info(self):
        print("[nodes]")
        print(f"    nodes num: {len(self.nodes)}")
        print("[2D element]")
        print(f"    2D elements num: {len(self.element_2D)}")
        print("[3D element]")
        print(f"    3D elements num: {len(self.elements)}")
        for material, comp in self.comps.items():
            if comp > 0:
                mask = self.element_comps[:]==comp
                print(f"    {material}: {np.count_nonzero(mask)}")
        