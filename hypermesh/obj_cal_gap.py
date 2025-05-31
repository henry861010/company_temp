import numpy as np

'''
    New fetaure in the future:
    1. obj type/name: the obj of gap is produced at the run time, if the user want to delete the action .fill_gap(), these obj should be mark to prevent uncorrected delete
        * or use the list to record the gap obj ???
    Consideration:
    1. now it supoort the "box" for the child objs which are filled the gap, how to support "cylinder"?
'''

### support only the "BOX" now
def fill_gap(self, material: str, gap: float, begin: float, end: float):
    table_x_dim = {} ### dim -> id
    table_y_dim = {} ### dim -> id
    table_x_id = {} ### id -> dim
    table_y_id = {} ### id -> dim

    ### sort the dim list (assign the 1 is unmeaning, it should to "regist" in the dict)
    for child_obj in self.child_objs:
        table_x_id[child_obj.face.dim[0]] = 1
        table_y_id[child_obj.face.dim[1]] = 1
        table_x_id[child_obj.face.dim[2]] = 1
        table_y_id[child_obj.face.dim[3]] = 1
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
    section_type = np.zeros((num_x-1, num_y-1)) 

    ### determine the "die" section 
    for child_obj in self.child_objs:
        node1_x_id = table_x_id[child_obj.face.dim[0]]
        node1_y_id = table_y_id[child_obj.face.dim[1]]
        node3_x_id = table_x_id[child_obj.face.dim[2]]
        node3_y_id = table_y_id[child_obj.face.dim[3]]
        for i in range(node1_x_id, node3_x_id):
            for j in range(node1_y_id, node3_y_id):
                section_type[i][j] = 1

    ### determine the "gap" section
    for i in range(0, section_num_x):
        for j in range(0, section_num_y):
            if section_type[i][j] == 0:
                ### x-axis
                if i>0 and section_type[i-1][j]:
                    right = i + 1
                    while 1:
                        if right >= section_num_x:
                            ### there is no die type at the right
                            right = -1
                            break
                        elif section_type[right][j]:
                            ### find the die
                            break
                        else:
                            ### continue to find
                            right += 1
                    if right != -1 and table_x_dim[right] - table_x_dim[i] <= gap:
                        ### if there is die at the right section, set all the empty area to fill
                        for k in range(i, right):
                            section_type[k][j] = 2

                 ### y-axis
                if j>0 and section_type[i][j-1]:
                    upper = j + 1
                    while 1:
                        if upper >= section_num_y:
                            upper = -1
                            break
                        elif section_type[i][upper]:
                            break
                        else:
                            upper += 1
                    if upper != -1 and table_y_dim[upper] - table_y_dim[j] <= gap:
                        for k in range(j, upper):
                            section_type[i][k] = 2

            ### add the lose one (only in x-axis ???)
            if section_type[i][j] == 2:
                left = i - 1
                while 1:
                    if left<0:
                        left = -1
                        break
                    elif section_type[left][j]:
                        left += 1
                        break
                    else:
                        left -= 1
                if left != -1 and table_x_dim[i] - table_x_dim[left] <= gap:
                    for k in range(left, i):
                        section_type[k][j] = 2
                    
                

    ### merge the gap section and regenerate the list
    ###     * merge algorithm ???
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
                
                child_obj = Obj(z = begin, type_ = "Box", dim = [node1_x_dim, node1_y_dim, node3_x_dim, node3_y_dim])
                child_obj.add_layer(thk = (end - begin), material = material)
                
                self.child_objs.append(child_obj)
