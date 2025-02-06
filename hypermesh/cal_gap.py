import matplotlib.pyplot as plt
import matplotlib.patches as patches
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
    for dim in dim_list:
        node1_x_id = table_x_id[dim[0]]
        node1_y_id = table_y_id[dim[1]]
        node3_x_id = table_x_id[dim[2]]
        node3_y_id = table_y_id[dim[3]]
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
                            right = -1
                            break
                        elif section_type[right][j]:
                            break
                        else:
                            right += 1
                    if right != -1 and table_x_dim[right] - table_x_dim[i] <= gap:
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
    gap_list = []
    for i in range(0, section_num_x):
        for j in range(0, section_num_y):
            if section_type[i][j] == 2:
                node1_x_dim = table_x_dim[i]
                node1_y_dim = table_y_dim[j]
                node3_x_dim = table_x_dim[i+1]
                node3_y_dim = table_y_dim[j+1]
                gap_list.append([node1_x_dim, node1_y_dim, node3_x_dim, node3_y_dim])

    return  gap_list

def print_dim(dim_list):
    print("x: ",end="")
    for dim in dim_list:
        print(f"[{dim[0]} {dim[2]}]",end=" ")
    print("")
    print("y: ",end="")
    for dim in dim_list:
        print(f"[{dim[1]} {dim[3]}]",end=" ")
    print("")

#gap = 3
#dim_list = [[0, 0, 1, 6], [6, 0, 8, 2], [4, 4, 8, 6]]
gap = 5
dim_list = [[0, 0, 1, 2], [0, 3, 2, 9], [5, 0, 7, 1], [5, 7, 7, 9]]
print_dim(dim_list)
gap_dim_list = cal_gap(gap, dim_list)
print_dim(gap_dim_list)


# Create figure and axis
fig, ax = plt.subplots()

# Background (white)
ax.set_facecolor("white")

# Draw the rectangles
max_x = 0
max_y = 0
for dim in dim_list:
    rect = patches.Rectangle((dim[0], dim[1]), dim[2]-dim[0], dim[3]-dim[1], color="black")
    ax.add_patch(rect)
    max_x = max(max_x, dim[2])
    max_y = max(max_y, dim[3])
for dim in gap_dim_list:
    rect = patches.Rectangle((dim[0], dim[1]), dim[2]-dim[0], dim[3]-dim[1], color="blue")
    ax.add_patch(rect)

# Set plot limits based on rectangle positions
ax.set_xlim(0, max_x)
ax.set_ylim(0, max_y)

plt.show()
