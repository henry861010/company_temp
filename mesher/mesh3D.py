import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

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
        self.elements = np.empty((0, ELEMENT_LEN), dtype=np.int32)
        self.element_ids = np.empty((0), dtype=np.int32)
        
        ### nodes
        self.nodes = np.empty((0, NODE_LEN), dtype=np.float64)
        self.node_ids = np.empty((0), dtype=np.float64)
        
        ### process
        self.element_2D = np.empty((0, ELEMENT_2D_LEN), dtype=np.float32)
        self.element_2D_nodes = np.empty((0, 4), dtype=np.int32)
        
    ### initial
    def initial(self, parser:'Mesh2D'):
        element_coords, element_node_ids, node_coords, node_ids = parser.get()
        self.element_2D = np.empty((len(element_coords), ELEMENT_2D_LEN), dtype=np.float32)
        
        self.element_2D[:,ELEMENT_2D_NODE1_X:ELEMENT_2D_NODE4_Y+1] = element_coords.reshape(element_coords.shape[0], 8)
        self.element_2D[:,ELEMENT_2D_COMP_ID] = 0
        self.element_2D_nodes = element_node_ids
        
        self.cal_volumns()
        
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
        
    def search_face(self, elements, typ, dim, index=None, eps=0.0):
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

        if typ == "BOX":
            bl_x, bl_y, tr_x, tr_y = dim
            if eps:
                bl_x -= eps
                bl_y -= eps
                tr_x += eps
                tr_y += eps
            return (min_x >= bl_x) & (max_x <= tr_x) & (min_y >= bl_y) & (max_y <= tr_y)

        elif typ == "CYLINDER":
            cx, cy, r = dim
            rr = r*r + 0.0
            if eps:
                rr = (r + eps) * (r + eps)
            dist = (x4 - cx)**2 + (y4 - cy)**2
            return np.all(dist <= rr, axis=1)

        else:
            raise ValueError(f"Unsupported type: {typ}")

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
            remaining_indices = np.setdiff1d(np.arange(len(elements)), chosen_indices, assume_unique=False)
            return chosen_indices, remaining_indices
        else:
            # no assignment if density threshold is 0 or vols too small
            return np.empty((0), dtype=np.int32), np.arange(len(elements))

    def organize(self, area: dict):
        # 1) Select the area once (mask -> indices)
        ranges = [{"type": area["type"], "dim": area["dim"]}]
        holes  = area.get("holes")
        area_indices  = self.search_faces(self.element_2D, ranges, holes)  # boolean over elements
        if len(area_indices) == 0:
            return

        # Working pool: local indices into area_idx
        remaining_indices = np.arange(len(area_indices), dtype=np.int32)

        # Convenience views for writes/reads via global IDs
        area_comps = self.element_2D[area_indices, ELEMENT_2D_COMP_ID]

        # Volumes for NORMAL metals (within area)
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
                    ### find the assiment area
                    (remaining_assigned_indices, remaining_unassigned_indices) = self.assign_metal(self.element_2D[area_indices][remaining_indices], density, volumn)
                    assigned_indices  = remaining_indices[remaining_assigned_indices]
                    unassigned_indices  = remaining_indices[remaining_unassigned_indices]
                    
                    ### assigne metal
                    material = metal["material"]
                    if material not in self.comps:
                        self.comps[material] = len(self.comps)
                    comp_id = self.comps[material]

                    self.element_2D[area_indices[assigned_indices], ELEMENT_2D_COMP_ID] = comp_id
                    remaining_indices = unassigned_indices

        ### assign the material
        if len(remaining_indices):
            material = area["material"]
            if material not in self.comps:
                self.comps[material] = len(self.comps)
            comp_id = self.comps[material]
            self.element_2D[area_indices[remaining_indices], ELEMENT_2D_COMP_ID] = comp_id
        
    def drag(self, element_size: float, end: float):
        print("drag")
        
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

    ### debug
    def show_info(self):
        print("[nodes]")
        print(f"    nodes num: {len(self.nodes)}")
        print("[2D element]")
        print(f"    2D elements num: {len(self.element_2D)}")
        print("[3D element]")
        print(f"    3D elements num: {len(self.elements)}")
        for material, comp in self.comps.items():
            mask = self.element_2D[:,ELEMENT_2D_COMP_ID]==comp
            print(f"    {material}: {np.count_nonzero(mask)}")
            
    def show_graph_2D(self, cmap='tab20'):
        patches = []
        colors = []

        for elem in self.element_2D:
            comp_id = int(elem[ELEMENT_2D_COMP_ID])
            coords = elem[ELEMENT_2D_NODE1_X:ELEMENT_2D_NODE4_Y+1].reshape(4, 2)   # shape (4,2): [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
            poly = Polygon(coords, closed=True)
            patches.append(poly)
            colors.append(comp_id)
        collection = PatchCollection(patches, cmap=cmap, edgecolor='k', alpha=0.8)
        collection.set_array(colors)

        fig, ax = plt.subplots()
        ax.add_collection(collection)
        ax.autoscale()  # fit to elements
        ax.set_aspect('equal', 'box')
        plt.colorbar(collection, ax=ax, label="comp_id")
        plt.show()
        