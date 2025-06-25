import numpy as np

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
def region_get_sturct(boundary_list: list):
    table_x_dim = {} ### dim -> id
    table_y_dim = {} ### dim -> id
    table_x_id = {} ### id -> dim
    table_y_id = {} ### id -> dim

    ### sort the dim list (assign the 1 is unmeaning, it should to "regist" in the dict)
    for boundary in boundary_list:
        table_x_id[boundary[0]] = 1
        table_y_id[boundary[1]] = 1
        table_x_id[boundary[2]] = 1
        table_y_id[boundary[3]] = 1
    num_x = len(table_x_id)
    num_y = len(table_y_id)
    section_num_x = num_x-1
    section_num_y = num_y-1
    table_x_id = dict(sorted(table_x_id.items()))
    table_y_id = dict(sorted(table_y_id.items()))

    ### create the table to record the relation between node and dim
    for index, dim_x in enumerate(table_x_id):
        table_x_id[dim_x] = index
        table_x_dim[index] = dim_x
    for index, dim_y in enumerate(table_y_id):
        table_y_id[dim_y] = index
        table_y_dim[index] = dim_y

    ### create the section
    ###     0: nothing
    ###     1: die
    ###     2: gap
    section_type = [[0 for _ in range(num_y - 1)] for _ in range(num_x - 1)]


    ### determine the "die" section 
    for boundary in boundary_list:
        node1_x_id = table_x_id[boundary[0]]
        node1_y_id = table_y_id[boundary[1]]
        node3_x_id = table_x_id[boundary[2]]
        node3_y_id = table_y_id[boundary[3]]
        for i in range(node1_x_id, node3_x_id):
            for j in range(node1_y_id, node3_y_id):
                section_type[i][j] = 1
                
    return {
        "section_type": section_type,
        "table_x_dim": table_x_dim,
        "table_y_dim": table_y_dim,
        "table_x_id": table_x_id,
        "table_y_id": table_y_id,
        "section_num_x": section_num_x,
        "section_num_y": section_num_y
    }

def _region_check_struct(region_struct: dict):
    if "section_type" not in region_struct:
        raise ValueError(f'[region]: region_struct lack "section_type"')
        if not isinstance(obj, list) and all(isinstance(row, list) for row in obj):
            raise ValueError(f'[region]: section_type shoould be 2D list')
    if "table_x_dim" not in region_struct:
        raise ValueError(f'[region]: region_struct lack "table_x_dim"')
    if "table_y_dim" not in region_struct:
        raise ValueError(f'[region]: region_struct lack "table_y_dim"')
    if "table_x_id" not in region_struct:
        raise ValueError(f'[region]: region_struct lack "table_x_id"')
    if "table_y_id" not in region_struct:
        raise ValueError(f'[region]: region_struct lack "table_y_id"')

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
def region_set_gap(region_struct: dict, gap: float, approximate: float = 0):
    def cal_gap(region_struct, gap, ref_map):
        section_type = region_struct["section_type"]
        table_x_dim = region_struct["table_x_dim"]
        table_y_dim = region_struct["table_y_dim"]
        table_x_id = region_struct["table_x_id"]
        table_y_id = region_struct["table_y_id"]
        section_num_x = region_struct["section_num_x"]
        section_num_y = region_struct["section_num_y"]
        
        for i in range(0, section_num_x):
            for j in range(0, section_num_y):
                if not section_type[i][j] & ref_map:
                    ### x-axis
                    if i>0 and section_type[i-1][j] & ref_map:
                        right = i + 1
                        while 1:
                            if right >= section_num_x:
                                ### there is no die type at the right
                                right = -1
                                break
                            elif section_type[right][j] & ref_map:
                                ### find the die
                                break
                            else:
                                ### continue to find
                                right += 1
                        if right != -1 and table_x_dim[right] - table_x_dim[i] <= gap:
                            ### if there is die at the right section, set all the empty area to fill
                            for k in range(i, right):
                                section_type[k][j] += 2

                    ### y-axis
                    if j>0 and section_type[i][j-1] & ref_map:
                        upper = j + 1
                        while 1:
                            if upper >= section_num_y:
                                upper = -1
                                break
                            elif section_type[i][upper] & ref_map:
                                break
                            else:
                                upper += 1
                        if upper != -1 and table_y_dim[upper] - table_y_dim[j] <= gap:
                            for k in range(j, upper):
                                section_type[i][k] += 2

                ### add the lose one (only in x-axis ???)
                if section_type[i][j] & (1 << 1):
                    left = i - 1
                    while 1:
                        if left<0:
                            left = -1
                            break
                        elif section_type[left][j] & ref_map:
                            left += 1
                            break
                        else:
                            left -= 1
                    if left != -1 and table_x_dim[i] - table_x_dim[left] <= gap:
                        for k in range(left, i):
                            section_type[k][j] += 2
        region_struct["section_type"] = section_type
        return region_struct
         
    ### check the structure of region_struct
    _region_check_struct(region_struct)
    
    ### determine the "gap" section
    ref_map = (1 << 1) + 1
    region_struct = cal_gap(region_struct, gap, ref_map)   
                   
    ### set the approximate
    if approximate > 0:
        ### set the 1 to 2
        for i in range(0, region_struct["section_num_x"]):
            for j in range(0, region_struct["section_num_y"]):
                if region_struct["section_type"][i][j] & 1:
                    region_struct["section_type"][i][j] += 2
        ref_map = (1 << 1) + 1
        region_struct = cal_gap(region_struct, approximate, ref_map)    
    
    return region_struct

'''
    merge the section_type in region_struct to "larger" section
    Note: it find the bounding at row firstly then find the upper bounding to build the larger region
    
    return: [[node1_x, node1_y, node3_x, node3_y], [], [], ...]
'''
def region_merge_section(region_struct: dict):
    ### check the structure of region_struct
    _region_check_struct(region_struct)
    
    section_type = region_struct["section_type"]
    table_x_dim = region_struct["table_x_dim"]
    table_y_dim = region_struct["table_y_dim"]
    table_x_id = region_struct["table_x_id"]
    table_y_id = region_struct["table_y_id"]
    section_num_x = region_struct["section_num_x"]
    section_num_y = region_struct["section_num_y"]
    
    ### gegion to merge region
    merged_boundary_list = []
    for i in range(0, section_num_x):
        for j in range(0, section_num_y):
            if section_type[i][j] == 2:
                ### find the rightest
                right = i + 1
                while right < section_num_x and section_type[right][j] == 2:
                        right += 1
                
                ### for each one layer(i~right-1) find the topest 
                upper = j + 1
                while upper < section_num_y:
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
                
                node1_x_dim = table_x_dim[i]
                node1_y_dim = table_y_dim[j]
                node3_x_dim = table_x_dim[right]
                node3_y_dim = table_y_dim[upper]
                
                merged_boundary_list.append([node1_x_dim, node1_y_dim, node3_x_dim, node3_y_dim])
    return merged_boundary_list

'''
    this function return
'''
def region_mesh_block(region_struct: dict):
    ### check the structure of region_struct
    _region_check_struct(region_struct)
    
    section_type = region_struct["section_type"]
    table_x_dim = region_struct["table_x_dim"]
    table_y_dim = region_struct["table_y_dim"]
    table_x_id = region_struct["table_x_id"]
    table_y_id = region_struct["table_y_id"]
    section_num_x = region_struct["section_num_x"]
    section_num_y = region_struct["section_num_y"]
    
    ### get the mesh block
    mesh_block_list = []
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
                mesh_block_list.append([x_list, y_list])
                print(f"{i} - {right}")
                print(f"{j} - {upper}")
                print(reference_node)
                print(ceil_table)
                print(x_list)
                print("")
    return mesh_block_list
