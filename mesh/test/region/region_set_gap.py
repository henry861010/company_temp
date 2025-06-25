import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from region import *

def print_dim(dim_list):
    print("x: ",end="")
    for dim in dim_list:
        print(f"[{dim[0]} {dim[2]}]",end=" ")
    print("")
    print("y: ",end="")
    for dim in dim_list:
        print(f"[{dim[1]} {dim[3]}]",end=" ")
    print("")

'''
### test1
gap = 3
dim_list = [[0, 0, 1, 6], [6, 0, 8, 2], [4, 4, 8, 6]]
region_struct = region_get_sturct(dim_list)
region_struct = region_set_gap(region_struct, gap)
gap_dim_list = region_merge_section(region_struct)
'''

'''
### test2
gap = 6
dim_list = [[0, 0, 1, 2], [0, 3, 2, 9], [5, 0, 7, 1], [5, 7, 7, 9]]
region_struct = region_get_sturct(dim_list)
region_struct = region_set_gap(region_struct, gap)
gap_dim_list = region_merge_section(region_struct)
'''

'''
### test3
gap = 3
dim_list = [[0, 0, 1, 10], [5, 0, 10, 3], [5, 6, 10, 10]]
region_struct = region_get_sturct(dim_list)
region_struct = region_set_gap(region_struct, gap)
gap_dim_list = region_merge_section(region_struct)
'''

### test4
gap = 3
approximate = 20
dim_list = [[0, 0, 3, 3], [4, 0, 6, 10], [20, 2, 24, 10]]
region_struct = region_get_sturct(dim_list)
region_struct = region_set_gap(region_struct, gap, approximate)
gap_dim_list = region_merge_section(region_struct)


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
