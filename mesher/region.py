import numpy as np
import math
from matplotlib.path import Path
import klayout.db as pya
import matplotlib.pyplot as plt

TYPE_EMPTY = 0
TYPE_DIE = 1
TYPE_TARGET = 2

'''
    cell_type: list (i,j)
        * the type of the cell
    cell_num_x: Int
        * the length of the x
    cell_num_y: Int
        * the length of the y
    table_x_dim: list
        * the i to x
    table_y_dim: list
        * the j to y
    face_list: face[]
        * the face of the target
    ref_face_list: face[]
        * the face of the reference
'''
class Region:
    def __init__(self, face_list:list=[], ref_face_list:list=[]):
        ### declare
        self.cell_type = np.empty((0,0), np.int16)
        self.cell_num_x = 0
        self.cell_num_y = 0
        self.table_x_dim = np.empty(0, np.float32)
        self.table_y_dim = np.empty(0, np.float32)
        
        self.face_list = []
        self.ref_face_list = []
        
        ### build the basic info
        if face_list:
            self.set(face_list, ref_face_list)
                            
    def _signed_area2(self, pts):
        """Twice the signed area. >0: CCW (Cartesian y-up), <0: CW."""
        s = 0.0
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            s += x1 * y2 - x2 * y1
        return s

    def _is_clockwise(self, poly):
        return self._signed_area2(poly) < 0.0  # flip if your y-axis is downward

    def _ensure_orientation(self, pts, want_cw):
        if len(pts) < 3:
            return pts
        a2 = self._signed_area2(pts)
        is_cw = (a2 < 0.0)
        if want_cw != is_cw:
            return pts[::-1]
        return pts

    def _poly_to_path(self, poly):
        """
        Build a closed Path for a single polygon of arbitrary length.
        Works with Path.make_compound_path(*paths).
        """
        n = len(poly)
        if n < 2:
            return Path(np.asarray(poly, float))
        verts = [tuple(p) for p in poly]
        codes = [Path.MOVETO] + [Path.LINETO] * (n - 1) + [Path.CLOSEPOLY]
        # CLOSEPOLY needs a dummy vertex; (0,0) is fine and ignored for filling
        verts = verts + [(0.0, 0.0)]
        return Path(np.asarray(verts, float), codes)
    
    ### publice
    def set(self, face_list=None, ref_face_list=None):
        if face_list is None:
            face_list = []
        if ref_face_list is None:
            ref_face_list = []

        total_face_list = face_list + ref_face_list

        # --- type checking (also fix quotes in f-string) ---
        for face in total_face_list:
            if face["type"] in ("BOX", "POLYGON"):
                continue
            raise ValueError(f'[Region] the face type {face["type"]} is not supported')

        # --- collect x/y breakpoints (unique, sorted) ---
        table_x_id, table_y_id = {}, {}
        for face in total_face_list:
            if face["type"] == "BOX":
                x0, y0, x1, y1 = face["dim"]
                table_x_id[x0] = 1; table_x_id[x1] = 1
                table_y_id[y0] = 1; table_y_id[y1] = 1
            else:  # POLYGON
                for x, y in face["dim"]:
                    table_x_id[x] = 1
                    table_y_id[y] = 1

        self.cell_num_x = len(table_x_id) - 1
        self.cell_num_y = len(table_y_id) - 1
        table_x_id = dict(sorted(table_x_id.items()))
        table_y_id = dict(sorted(table_y_id.items()))

        # --- build id <-> coord tables ---
        self.table_x_dim = np.empty(self.cell_num_x + 1, np.float32)  # id -> x
        self.table_y_dim = np.empty(self.cell_num_y + 1, np.float32)  # id -> y
        for i, x in enumerate(table_x_id):
            table_x_id[x] = i
            self.table_x_dim[i] = x
        for j, y in enumerate(table_y_id):
            table_y_id[y] = j
            self.table_y_dim[j] = y

        # --- init cell types ---
        self.cell_type = np.zeros((self.cell_num_x, self.cell_num_y), dtype=np.int16)

        # --- cell centers ---
        x = np.asarray(self.table_x_dim)
        y = np.asarray(self.table_y_dim)
        cx = 0.5 * (x[:-1] + x[1:])
        cy = 0.5 * (y[:-1] + y[1:])
        CX, CY = np.meshgrid(cx, cy, indexing='ij')
        points = np.c_[CX.ravel(), CY.ravel()]  # (N,2)

        # === Build die mask with "CW = hull", "CCW = hole" ===
        die_mask = np.zeros(CX.shape, dtype=bool)

        # 1) BOXes behave as hulls (union)
        for face in face_list:
            if face["type"] == "BOX":
                x0, y0, x1, y1 = face["dim"]
                idx = (x0 < CX) & (CX < x1) & (y0 < CY) & (CY < y1)
                die_mask |= idx

        # 2) Split polygons by orientation
        hull_paths, hole_paths = [], []
        for face in face_list:
            if face["type"] == "POLYGON":
                poly = face["dim"]
                if self._is_clockwise(poly):     # CW => hull
                    hull_paths.append(self._poly_to_path(poly))
                else:                       # CCW => hole
                    hole_paths.append(self._poly_to_path(poly))

        # 3) Union all hull polygons
        if hull_paths:
            hull_path = Path.make_compound_path(*hull_paths)  # accepts variable-length polys
            inside_hulls = hull_path.contains_points(points).reshape(CX.shape)
            die_mask |= inside_hulls

        # 4) Subtract all holes
        if hole_paths:
            hole_path = Path.make_compound_path(*hole_paths)
            inside_holes = hole_path.contains_points(points).reshape(CX.shape)
            die_mask &= ~inside_holes

        # 5) Commit mask
        self.cell_type[die_mask] = TYPE_DIE
    
    ### set    
    def set_gap(self, gap, target_mask=TYPE_DIE):
        for i in range(0, self.cell_num_x):
            for j in range(0, self.cell_num_y):
                if not self.cell_type[i][j] & target_mask:
                    ### x-axis
                    if i>0 and self.cell_type[i-1][j] & target_mask:
                        right = i + 1
                        while 1:
                            if right >= self.cell_num_x:
                                ### there is no die type at the right
                                right = -1
                                break
                            elif self.cell_type[right][j] & target_mask:
                                ### find the die
                                break
                            else:
                                ### continue to find
                                right += 1
                        if right != -1 and self.table_x_dim[right] - self.table_x_dim[i] <= gap:
                            ### if there is die at the right cell, set all the empty area to fill
                            for k in range(i, right):
                                self.cell_type[k][j] |= TYPE_TARGET

                    ### y-axis
                    if j>0 and self.cell_type[i][j-1] & target_mask:
                        upper = j + 1
                        while 1:
                            if upper >= self.cell_num_y:
                                upper = -1
                                break
                            elif self.cell_type[i][upper] & target_mask:
                                break
                            else:
                                upper += 1
                        if upper != -1 and self.table_y_dim[upper] - self.table_y_dim[j] <= gap:
                            for k in range(j, upper):
                                self.cell_type[i][k] |= TYPE_TARGET

                ### add the lose one (only in x-axis ???)
                if self.cell_type[i][j] & 2:
                    left = i - 1
                    while 1:
                        if left<0:
                            left = -1
                            break
                        elif self.cell_type[left][j] & target_mask:
                            left += 1
                            break
                        else:
                            left -= 1
                    if left != -1 and self.table_x_dim[i] - self.table_x_dim[left] <= gap:
                        for k in range(left, i):
                            self.cell_type[k][j] |= TYPE_TARGET
   
    def set_edge(self, gap):
        INT_MAX = 1000000
        def vertical(left, right, j):
            if left == -1:
                return j, j, INT_MAX
            if right == self.cell_num_x:
                return j, j, INT_MAX
            
            target_mask = TYPE_DIE | TYPE_TARGET
            
            ### find top
            top = j
            while top < self.cell_num_y:
                if self.cell_type[left][top]&target_mask and self.cell_type[right][top]&target_mask:
                    break
                elif not self.cell_type[left][top]&target_mask and not self.cell_type[right][top]&target_mask:
                    break
                top += 1
            ### find bottom
            bottom = j
            while 0 <= bottom:
                if self.cell_type[left][bottom]&target_mask and self.cell_type[right][bottom]&target_mask:
                    break
                elif not self.cell_type[left][bottom]&target_mask and not self.cell_type[right][bottom]&target_mask:
                    break
                bottom -= 1
            return bottom, top, self.table_y_dim[top]-self.table_y_dim[bottom+1]

        def horizon(bottom, top, i):
            if bottom == -1:
                return i, i, INT_MAX
            if top == self.cell_num_y:
                return i, i, INT_MAX
            
            target_mask = TYPE_DIE | TYPE_TARGET
            
            ### find top
            right = i
            while right < self.cell_num_x:
                if self.cell_type[right][bottom]&target_mask and self.cell_type[right][top]&target_mask:
                    break
                elif not self.cell_type[right][bottom]&target_mask and not self.cell_type[right][top]&target_mask:
                    break
                right += 1

            ### find bottom
            left = i
            while 0 <= left:
                if self.cell_type[left][bottom]&target_mask and self.cell_type[left][top]&target_mask:
                    break
                elif not self.cell_type[left][bottom]&target_mask and not self.cell_type[left][top]&target_mask:
                    break
                left -= 1
            return left, right, self.table_x_dim[right]-self.table_x_dim[left+1]
        
        target_mask = TYPE_DIE | TYPE_TARGET
        isChange = False
        while True:
            isSet = False
            for i in range(0, self.cell_num_x):
                for j in range(0, self.cell_num_y):
                    if self.cell_type[i][j] & target_mask:
                        ### go right
                        if i+1 < self.cell_num_x and not self.cell_type[i+1][j] & target_mask:
                            bottom, top, l = vertical(i, i+1, j)
                            if l <= gap:
                                _, bottom_right, _ = horizon(bottom, bottom+1, i+1)
                                _, top_right, _ = horizon(top-1, top, i+1)
                                right = max(top_right, bottom_right)
                                index = i+1
                                while index < right:
                                    isSet = True
                                    isChange = True
                                    self.cell_type[index,bottom+1:top] |= TYPE_TARGET
                                    index += 1
                        ### go left
                        if 0 <= i-1 and not self.cell_type[i-1][j] & target_mask:
                            bottom, top, l = vertical(i-1, i, j)
                            if l <= gap:
                                bottom_left, _, _ = horizon(bottom, bottom+1, i-1)
                                top_left, _, _ = horizon(top-1, top, i-1)
                                left = min(top_left, bottom_left)
                                index = i-1
                                while left < index:
                                    isSet = True
                                    isChange = True
                                    self.cell_type[index,bottom+1:top] |= TYPE_TARGET
                                    index -= 1
                        ### go top
                        if j+1 < self.cell_num_y and not self.cell_type[i][j+1] & target_mask:
                            left, right, l = horizon(j, j+1, i)
                            if l <= gap:
                                _, right_top, _ = vertical(left, left+1, j+1)
                                _, left_top, _ = vertical(right-1, right, j+1)
                                top = max(left_top, right_top)
                                index = j+1
                                while index < top:
                                    isSet = True
                                    isChange = True
                                    self.cell_type[left+1:right,index] |= TYPE_TARGET
                                    index += 1
                        ### go bottom
                        if 0 <= j-1 and not self.cell_type[i][j-1] & target_mask:
                            left, right, l = horizon(j-1, j, i)
                            if l <= gap:
                                right_bottom, _, _ = vertical(left, left+1, j-1)
                                left_bottom, _, _ = vertical(right-1, right, j-1)
                                bottom = min(left_bottom, right_bottom)
                                index = j-1
                                while bottom < index:
                                    isSet = True
                                    isChange = True
                                    self.cell_type[left+1:right,index] |= TYPE_TARGET
                                    index -= 1

            if not isSet:
                break
        return isChange
    
    def set_round(self, gap):
        while True:
            self.set_gap(gap*2)
            isSet = self.set_edge(gap)    
            if not isSet:
                break
    
    def set_clear(self, clear_mask=TYPE_TARGET):
        for i in range(0, self.cell_num_x):
            for j in range(0, self.cell_num_y):
                if self.cell_type[i][j] & clear_mask:
                    self.cell_type[i][j] = TYPE_EMPTY
        
    ### get
    def get_outline(self, target_mask=TYPE_TARGET, isDetail=False):
        dbu = 1
        region = pya.Region()
        for i in range(self.cell_num_x):
            for j in range(self.cell_num_y):
                if self.cell_type[i][j] & target_mask:
                    x1 = int(self.table_x_dim[i]   / dbu)
                    y1 = int(self.table_y_dim[j]   / dbu)
                    x3 = int(self.table_x_dim[i+1] / dbu)
                    y3 = int(self.table_y_dim[j+1] / dbu)
                    region.insert(pya.Box(x1, y1, x3, y3))

        polygon_list = []
        if isDetail:
            for poly in region.each_merged():
                polygon = {
                    "type": "POLYGON",
                    "dim": [],
                    "holes": []
                }
    
                # Hull points (force CW)
                hull = [[node.x * dbu, node.y * dbu] for node in poly.each_point_hull()]
                polygon["dim"] = self._ensure_orientation(hull, want_cw=True)

                # Hole points (force CCW)
                for h in range(poly.holes()):
                    hole = [[node.x * dbu, node.y * dbu] for node in poly.each_point_hole(h)]
                    polygon["holes"].append(self._ensure_orientation(hole, want_cw=False))
                polygon_list.append(polygon)
        else:
            for poly in region.each_merged():
                # Hull points (force CW)
                hull = [[node.x * dbu, node.y * dbu] for node in poly.each_point_hull()]
                polygon_list.append(self._ensure_orientation(hull, want_cw=True))

                # Hole points (force CCW)
                for h in range(poly.holes()):
                    hole = [[node.x * dbu, node.y * dbu] for node in poly.each_point_hole(h)]
                    polygon_list.append(self._ensure_orientation(hole, want_cw=False))
        return polygon_list

    def get_mesh_blocks(self, mask: int = 2):
        ### get the mesh block
        mesh_block_list = []
        ceil_table = [self.cell_num_y for _ in self.cell_type]
        reference_node = [False for _ in self.table_x_dim]
        record_visit = [[False] * len(row) for row in self.cell_type]
        
        for j in range(0, self.cell_num_y):
            for i in range(0, self.cell_num_x):
                if self.cell_type[i][j] & mask and not record_visit[i][j]:
                    x_list = [] ### record the reference node for this block
                    y_list = [] ### record the reference node for this block
                    
                    ### find the rightest
                    right = i + 1
                    while right < self.cell_num_x and self.cell_type[right][j] & mask:
                        right += 1
                        
                    ### find the ceil of each cell (only execute while begin at y)
                    upper = self.cell_num_y
                    for m in range(i, right):
                        if j == 0 or not self.cell_type[m][j-1] & mask:
                            ### find the ceil
                            n = j + 1
                            while n < self.cell_num_y and self.cell_type[m][n] & mask:
                                n += 1
                            ceil_table[m] = n
                            
                        ### find the lowest ceil
                        upper = min(upper, ceil_table[m])
                        
                        ### find the ref x of the ref_line which y between the (j~upper)
                        print("~~~~~~~~~")
                    
                    ### find left wall height (u, if we don't care wall height, the upper would higher than left and right wall)
                    if i > 1 and not self.cell_type[i-1][j] & mask:
                        n = j + 1
                        while n < self.cell_num_y and not self.cell_type[i-1][n] & mask:
                            n += 1
                        upper = min(upper, n)
                    
                    ### find right wall height
                    if right != self.cell_num_x and not self.cell_type[right][j] & mask:
                        n = j + 1
                        while n < self.cell_num_y and not self.cell_type[right][n] & mask:
                            n += 1
                        upper = min(upper, n)
                    
                    ### determine the reference node
                    for m in range(i+1, right-1):
                        ### clear the reference mark if y begin
                        if j==0 or self.cell_type[m][j-1] & mask == 0:
                            if self.cell_type[m-1][j-1] & mask == 0:
                                reference_node[m] = False
                            if self.cell_type[m+1][j-1] & mask == 0:
                                reference_node[m+1] = False
                        
                        ### set the reference node
                        if ceil_table[m] != ceil_table[m-1]:
                            reference_node[m] = True
                        if ceil_table[m] != ceil_table[m+1]:
                            reference_node[m+1] = True
                            
                    reference_node[i] = True
                    reference_node[right] = True

                    ### set the visited cell to true 
                    for m in range(i, right):
                        for n in range(j, upper):
                            record_visit[m][n] = True

                    ### build the x_list & y_list
                    y_list = [self.table_y_dim[j], self.table_y_dim[upper]]
                    x_list = []
                    for m in range(i, right+1):
                        if reference_node[m]:
                            x_list.append(self.table_x_dim[m])
                            
                    ### build the block 
                    mesh_block_list.append([x_list, y_list])
                    print(f"{i} - {right}")
                    print(f"{j} - {upper}")
                    print(reference_node)
                    print(ceil_table)
                    print(x_list)
                    print("")
        return mesh_block_list

    def get_mesh_meshmodel2(self, element_size: float, expanding_num: float, gap: float = 500, ifFixSize: bool = True):
        x_list = []
        y_list = []
        return (x_list, y_list)
    
    ### debug
    def show_graph(self, x_list: list = [], y_list: list = []):
        cell_array = np.array(self.cell_type, copy=True)
        X, Y = np.meshgrid(self.table_x_dim, self.table_y_dim)

        cmap = plt.get_cmap('tab10')
        cell_array[(cell_array & 2)!=0] = 2
        plt.pcolormesh(X, Y, cell_array.T, cmap=cmap, edgecolors='k', shading='flat')
        
        # Add vertical lines
        for x in x_list:
            plt.plot([x, x], [self.table_y_dim[0], self.table_y_dim[-1]], color='red', linewidth=0.5)

        # Add horizontal lines
        for y in y_list:
            plt.plot([self.table_x_dim[0], self.table_x_dim[-1]], [y, y], color='red', linewidth=0.5)

        plt.gca().set_aspect('equal')
        plt.title("cell Status Map")
        plt.xlabel("X")
        plt.ylabel("Y")

        plt.show()
        
element_size = 1.5*5

### test1
region_obj = Region()
face1 = {
    "type": "POLYGON",
    "dim": [[0,0],[0,30],[30,30],[30,0]] 
}
face2 = {
    "type": "POLYGON",
    "dim": [[10,10],[20,10],[20,20],[10,20]] 
}
region_obj.set(face_list=[face1, face2])
region_obj.show_graph()

a = region_obj.get_outline(target_mask=TYPE_DIE, isDetail=True)
print(a)
    

    