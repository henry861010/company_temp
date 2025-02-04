import numpy as np

def cal_gap(gap, dim_list):
    table_x_dim = {}
    table_y_dim = {}
    table_x_id = {}
    table_y_id = {}

    ### sort the dim list
    for dim in dim_list:
        table_x_id[dim[0]] = 1
        table_y_id[dim[1]] = 1
        table_x_id[dim[2]] = 1
        table_y_id[dim[3]] = 1
    num_x = len(table_x_id)
    num_y = len(table_y_id)
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
    for dim in dim_list:
        node1_x_id = table_x_id[dim[0]]
        node1_y_id = table_y_id[dim[1]]
        node3_x_id = table_x_id[dim[2]]
        node3_y_id = table_y_id[dim[3]]
        for i in range(node1_x_id, node3_x_id):
            for j in range(node1_y_id, node3_y_id):
                section_type[i][j] = 1

    ### determine the "gap" section
    for i in range(0, num_x-1):
        for j in range(0, num_y-1):
            if section_type[i][j] == 0:
                if (
                    0 < i and i < num_x-1 and
                    section_type[i-1][j] == 1 and 
                    section_type[i+1][j] == 1 and 
                    (table_x_dim[i] - table_x_dim[i-1]) <= gap and
                    (table_x_dim[i+1] - table_x_dim[i]) <= gap
                ):
                    section_type[i][j] = 2
                elif (
                    0 < j and j < num_y-1 and
                    section_type[i][j-1] == 1 and 
                    section_type[i][j+1] == 1 and 
                    (table_y_dim[j] - table_y_dim[j-1]) <= gap and
                    (table_y_dim[j+1] - table_y_dim[j]) <= gap
                ):
                    section_type[i][j] = 2

    ### merge the gap section and regenerate the list
    ###     * merge algorithm ???
    gap_list = []
    for i in range(0, num_x-1):
        for j in range(0, num_y-1):
            if section_type[i][j] == 2:
                node1_x_dim = table_x_dim[i]
                node1_y_dim = table_y_dim[j]
                node3_x_dim = table_x_dim[i+1]
                node3_y_dim = table_y_dim[j+1]
                gap_list.append([node1_x_dim, node1_y_dim, node3_x_dim, node3_y_dim])

    return  gap_list


gap = 2
dim_list = [[0, 0, 2, 2], [3, 0, 5, 2], [6, 0, 8, 2], [16, 0, 18, 2]]
a = cal_gap(gap, dim_list)
print(a)