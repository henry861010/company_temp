import numpy as np
import math
from my_math import *

'''
    boundary_list: [boundary]
        * boundary: [node1_x, node1_y, node3_x, node3_y]
        
    return: {
        section_type[][]: 
            * 1bit: if there is it empty
            * 2bit: if target added
        table_x_dim[]
        table_y_dim[]
        table_x_id[]
        table_y_id[]
    }
'''
    
class Region:
    def __init__(self, boundary_list: list = [], ref_boundary_list: list = [], algorithm: str = "NORMAL"):
        ### declare
        self.section_type = []
        self.section_num_x = []
        self.section_num_y = []
        self.table_x_dim = []
        self.table_y_dim = []
        
        self.ref_line_x = []
        self.ref_line_y = []
        
        ### build the basic info
        if boundary_list:
            self.set_sturct(boundary_list)
            
        ### build reference line
        if ref_boundary_list:
            if algorithm == "NORMAL":
                for ref_boundary in ref_boundary_list:
                    self.ref_line_y.append([[ref_boundary[0], ref_boundary[1]], [ref_boundary[0], ref_boundary[3]]])
                    self.ref_line_y.append([[ref_boundary[2], ref_boundary[1]], [ref_boundary[2], ref_boundary[3]]])
                    self.ref_line_x.append([[ref_boundary[0], ref_boundary[1]], [ref_boundary[2], ref_boundary[1]]])
                    self.ref_line_x.append([[ref_boundary[0], ref_boundary[3]], [ref_boundary[2], ref_boundary[3]]])
            elif algorithm == "CHECKERBOARD":
                for ref_boundary in ref_boundary_list:
                    self.ref_line_y.append([[ref_boundary[0], -1e6], [ref_boundary[0], 1e6]])
                    self.ref_line_y.append([[ref_boundary[2], -1e6], [ref_boundary[2], 1e6]])
                    self.ref_line_x_list.append([[-1e6, ref_boundary[1]], [1e6, ref_boundary[1]]])
                    self.ref_line_x_list.append([[-1e6, ref_boundary[3]], [1e6, ref_boundary[3]]])
            self.ref_line_x.sort(key=lambda item: item[1])
            self.ref_line_y.sort(key=lambda item: item[0])
                    
    def set_sturct(self, boundary_list: list):
        self.table_x_dim = {} ### id -> dim
        self.table_y_dim = {} ### id -> dim
        table_x_id = {} ### dim -> id
        table_y_id = {} ### dim -> id

        ### sort the dim list (assign the 1 is unmeaning, it should to "regist" in the dict)
        for boundary in boundary_list:
            table_x_id[boundary[0]] = 1
            table_y_id[boundary[1]] = 1
            table_x_id[boundary[2]] = 1
            table_y_id[boundary[3]] = 1
        num_x = len(table_x_id)
        num_y = len(table_y_id)
        self.section_num_x = num_x-1
        self.section_num_y = num_y-1
        table_x_id = dict(sorted(table_x_id.items()))
        table_y_id = dict(sorted(table_y_id.items()))

        ### create the table to record the relation between node and dim
        for index, dim_x in enumerate(table_x_id):
            table_x_id[dim_x] = index
            self.table_x_dim[index] = dim_x
        for index, dim_y in enumerate(table_y_id):
            table_y_id[dim_y] = index
            self.table_y_dim[index] = dim_y

        ### create the section
        ###     0: nothing
        ###     1: die
        ###     2: gap
        self.section_type = [[0 for _ in range(num_y - 1)] for _ in range(num_x - 1)]


        ### determine the "die" section 
        for boundary in boundary_list:
            node1_x_id = table_x_id[boundary[0]]
            node1_y_id = table_y_id[boundary[1]]
            node3_x_id = table_x_id[boundary[2]]
            node3_y_id = table_y_id[boundary[3]]
            for i in range(node1_x_id, node3_x_id):
                for j in range(node1_y_id, node3_y_id):
                    self.section_type[i][j] = 1

    def set_decode_struct(self, section_type: list, table_x_dim: list, table_y_dim: list):
        self.section_type = section_type
        self.table_x_dim = table_x_dim
        self.table_y_dim = table_y_dim
        self.section_num_x = len(section_type)
        self.section_num_y = len(section_type[0])
        
    '''
        read the region_struct and set the section_type[i][j] to 2(fill comp) if it is in gap region
        return: {
            section_type
            table_x_dim
            table_y_dim
            table_x_id
            table_y_id
        }
    '''
    def set_gap(self, gap: float, approximate: float = 0):
        def cal_gap(gap, target_mask):
            for i in range(0, self.section_num_x):
                for j in range(0, self.section_num_y):
                    if not self.section_type[i][j] & target_mask:
                        ### x-axis
                        if i>0 and self.section_type[i-1][j] & target_mask:
                            right = i + 1
                            while 1:
                                if right >= self.section_num_x:
                                    ### there is no die type at the right
                                    right = -1
                                    break
                                elif self.section_type[right][j] & target_mask:
                                    ### find the die
                                    break
                                else:
                                    ### continue to find
                                    right += 1
                            if right != -1 and self.table_x_dim[right] - self.table_x_dim[i] <= gap:
                                ### if there is die at the right section, set all the empty area to fill
                                for k in range(i, right):
                                    self.section_type[k][j] += 2

                        ### y-axis
                        if j>0 and self.section_type[i][j-1] & target_mask:
                            upper = j + 1
                            while 1:
                                if upper >= self.section_num_y:
                                    upper = -1
                                    break
                                elif self.section_type[i][upper] & target_mask:
                                    break
                                else:
                                    upper += 1
                            if upper != -1 and self.table_y_dim[upper] - self.table_y_dim[j] <= gap:
                                for k in range(j, upper):
                                    self.section_type[i][k] += 2

                    ### add the lose one (only in x-axis ???)
                    if self.section_type[i][j] & 2:
                        left = i - 1
                        while 1:
                            if left<0:
                                left = -1
                                break
                            elif self.section_type[left][j] & target_mask:
                                left += 1
                                break
                            else:
                                left -= 1
                        if left != -1 and self.table_x_dim[i] - self.table_x_dim[left] <= gap:
                            for k in range(left, i):
                                self.section_type[k][j] += 2
                    
        ### determine the "gap" section
        target_mask = 1
        cal_gap(gap, target_mask)   
                    
        ### set the approximate
        if approximate > 0:
            target_mask = 2
            cal_gap(approximate, target_mask)

    '''
        merge the section_type in region_struct to "larger" section
        Note: it find the bounding at row firstly then find the upper bounding to build the larger region
        
        return: [[node1_x, node1_y, node3_x, node3_y], [], [], ...]
    '''
    def get_merge_section(self):
        ### deep copy the section_type(2D list)
        section_type = [row[:] for row in self.section_type]
        
        ### gegion to merge region
        merged_boundary_list = []
        for i in range(0, self.section_num_x):
            for j in range(0, self.section_num_y):
                if section_type[i][j] == 2:
                    ### find the rightest
                    right = i + 1
                    while right < self.section_num_x and section_type[right][j] == 2:
                            right += 1
                    
                    ### for each one layer(i~right-1) find the topest 
                    upper = j + 1
                    while upper < self.section_num_y:
                        valid_layer = True
                        for k in range(i, right):
                            if section_type[k][upper] != 2:
                                valid_layer = False
                                break
                        if valid_layer:
                            for k in range(i, right):
                                section_type[k][upper] = 0
                            upper += 1
                        else:
                            break
                    
                    node1_x_dim = self.table_x_dim[i]
                    node1_y_dim = self.table_y_dim[j]
                    node3_x_dim = self.table_x_dim[right]
                    node3_y_dim = self.table_y_dim[upper]
                    
                    merged_boundary_list.append([node1_x_dim, node1_y_dim, node3_x_dim, node3_y_dim])
        return merged_boundary_list

    '''
        this function return
    '''
    def get_mesh_block(self, mask: int = 2):
        ### get the mesh block
        mesh_block_list = []
        ceil_table = [self.section_num_y for _ in self.section_type]
        reference_node = [False for _ in self.table_x_dim]
        record_visit = [[False] * len(row) for row in self.section_type]
        
        for j in range(0, self.section_num_y):
            for i in range(0, self.section_num_x):
                if self.section_type[i][j] & mask and not record_visit[i][j]:
                    x_list = [] ### record the reference node for this block
                    y_list = [] ### record the reference node for this block
                    
                    ### find the rightest
                    right = i + 1
                    while right < self.section_num_x and self.section_type[right][j] & mask:
                        right += 1
                        
                    ### find the ceil of each section (only execute while begin at y)
                    upper = self.section_num_y
                    for m in range(i, right):
                        if j == 0 or not self.section_type[m][j-1] & mask:
                            ### find the ceil
                            n = j + 1
                            while n < self.section_num_y and self.section_type[m][n] & mask:
                                n += 1
                            ceil_table[m] = n
                            
                        ### find the lowest ceil
                        upper = min(upper, ceil_table[m])
                        
                        ### find the ref x of the ref_line which y between the (j~upper)
                        print("~~~~~~~~~")
                    
                    ### find left wall height (u, if we don't care wall height, the upper would higher than left and right wall)
                    if i > 1 and not self.section_type[i-1][j] & mask:
                        n = j + 1
                        while n < self.section_num_y and not self.section_type[i-1][n] & mask:
                            n += 1
                        upper = min(upper, n)
                    
                    ### find right wall height
                    if right != self.section_num_x and not self.section_type[right][j] & mask:
                        n = j + 1
                        while n < self.section_num_y and not self.section_type[right][n] & mask:
                            n += 1
                        upper = min(upper, n)
                    
                    ### determine the reference node
                    for m in range(i+1, right-1):
                        ### clear the reference mark if y begin
                        if j==0 or self.section_type[m][j-1] & mask == 0:
                            if self.section_type[m-1][j-1] & mask == 0:
                                reference_node[m] = False
                            if self.section_type[m+1][j-1] & mask == 0:
                                reference_node[m+1] = False
                        
                        ### set the reference node
                        if ceil_table[m] != ceil_table[m-1]:
                            reference_node[m] = True
                        if ceil_table[m] != ceil_table[m+1]:
                            reference_node[m+1] = True
                            
                    reference_node[i] = True
                    reference_node[right] = True

                    ### set the visited section to true 
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

    '''
        clear all target
    '''
    def region_clear_all(self):
        for i in range(len(section_type)):
            for j in range(len(section_type[0])):
                self.section_type[i][j] = self.section_type[i][j] & ~2

    '''
        find the outline list
    '''
    def region_get_outline(self, mask = 2):
        ### rotate direction
        def rotate(v, degree):
            tolerance = 0.001
            x = v[0]
            y = v[1]
            theta_rad = math.radians(-degree)  # Convert to radians
            x_new = x * math.cos(theta_rad) - y * math.sin(theta_rad)
            y_new = x * math.sin(theta_rad) + y * math.cos(theta_rad)
            if abs(x_new) < tolerance:
                x_new = 0
            if abs(y_new) < tolerance:
                y_new = 0
            return [int(x_new), int(y_new)]
        
        ### identity if the section_type[i][j] is empty or target(2)
        def section_status(section_type, i, j):
            if i < 0 or i >= len(section_type):
                return False
            if j < 0 or j >= len(section_type[0]):
                return False
            return section_type[i][j] & mask
        
        ### get end point
        def get_end_point(dir, i, j):
            if dir[0] == 0  and dir[1] == 1:
                return [i, j+1]
            elif dir[0] == 0  and dir[1] == -1:
                return [i+1, j]
            elif dir[0] == -1  and dir[1] == 0:
                return [i, j]
            elif dir[0] == 1  and dir[1] == 0:
                return [i+1, j+1]
            else:
                print("[region_get_outline - get_end_point] UNKNOW")
            
        ### clear the connected
        def clear_connected_section(section_type, i, j, clear_mask = 2):
            if i < 0 or i >= len(section_type):
                return
            if j < 0 or j >= len(section_type[0]):
                return
            if not section_type[i][j] & clear_mask:
                return 
            section_type[i][j] = section_type[i][j] & ~clear_mask
            region_clear_connected_section(section_type, i+1, j)
            region_clear_connected_section(section_type, i, j+1)
            region_clear_connected_section(section_type, i-1, j)
            region_clear_connected_section(section_type, i, j-1)           
            
        ### deep copy the section_type(2D list)
        section_type = [row[:] for row in self.section_type]
        
        ### find the outline
        outline_list_list = [] 
        for i in range(0, self.section_num_x):
            for j in range(0, self.section_num_y):
                if section_type[i][j] & mask:
                    ### set the dirst
                    outline_list = [] 
                    first_i = i
                    first_j = j
                    begin_point = [self.table_x_dim[i], self.table_y_dim[j]]
                    dir_now = [0, 1]
                    
                    while True:
                        ### convert to formal format
                        dir_270 = rotate(dir_now, 270)
                        
                        b_i = dir_270[0] + dir_now[0] + i
                        b_j = dir_270[1] + dir_now[1] + j
                        c_i = dir_now[0] + i
                        c_j = dir_now[1] + j
                        
                        ### rotate 270 (rotate 270 & vary i-j & add new outline)
                        if section_status(section_type, b_i, b_j) and section_status(section_type, c_i, c_j):
                            ### add the new outline
                            res = get_end_point(dir_now, i, j)
                            end_point = [self.table_x_dim[res[0]], self.table_y_dim[res[1]]]
                            outline_list.append([begin_point, end_point])
                            begin_point = end_point
                            
                            ### vary the direction & i-j
                            i += (dir_270[0] + dir_now[0])
                            j += (dir_270[1] + dir_now[1])
                            dir_now = dir_270
                            
                        ### rotate 90 (rotate 90 & same i-j & add new outline)
                        elif not section_status(section_type, c_i, c_j):
                            ### add the new outline
                            res = get_end_point(dir_now, i, j)
                            end_point = [self.table_x_dim[res[0]], self.table_y_dim[res[1]]]
                            outline_list.append([begin_point, end_point])
                            begin_point = end_point
                            
                            ### vary the direction & i-j
                            dir_now = rotate(dir_now, 90)
                            
                        ### go through (same dir & vary i-j)
                        else:
                            i += dir_now[0]
                            j += dir_now[1]
                            
                        if i == first_i and j == first_j and dir_now[0] == 0 and dir_now[1] == 1:
                            break
                        
                    ### append the outline of the block to the outline_list_list (multiple outline)
                    outline_list_list.append(outline_list)
                    
                    ### clear the found to prevent the duplicate seach
                    clear_connected_section(section_type, i, j, mask)
        return outline_list_list