import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from region import *

'''
section_type = [
    [0, 2, 2, 2, 2, 2, 0, 0, 0, 0],
    [0, 2, 2, 2, 2, 2, 0, 0, 0, 0],
    [0, 0, 0, 2, 2, 2, 0, 2, 0, 0],
    [0, 0, 0, 2, 2, 2, 0, 2, 2, 2],
    [0, 2, 2, 2, 2, 2, 0, 2, 2, 2],
    [0, 2, 2, 2, 2, 2, 0, 2, 0, 0],
    [0, 0, 0, 0, 2, 2, 2, 2, 2, 2],
    [0, 0, 0, 0, 2, 2, 0, 2, 2, 2],
    [0, 0, 0, 0, 2, 2, 0, 2, 2, 2],
    [0, 0, 0, 0, 2, 2, 0, 0, 0, 0]
]
'''

'''
section_type = [
    [2, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 2, 2, 0, 0, 0, 0],
    [0, 0, 0, 2, 2, 2, 0, 0, 0, 0],
    [0, 0, 0, 2, 2, 2, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]
'''

section_type = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 2, 0, 0, 0, 0, 0, 0],
    [0, 2, 2, 2, 2, 2, 0, 0, 0, 0],
    [0, 2, 2, 2, 2, 2, 0, 0, 0, 0],
    [0, 2, 2, 2, 2, 2, 0, 0, 0, 0],
    [0, 0, 2, 2, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 2, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]


table_x_dim = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
table_y_dim = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

region_struct = {}
region_struct["section_type"] = section_type
region_struct["section_num_x"] = len(section_type)
region_struct["section_num_y"] = len(section_type[0])
region_struct["table_x_dim"] = table_x_dim
region_struct["table_y_dim"] = table_y_dim
region_struct["table_x_id"] = []
region_struct["table_y_id"] = []

outline = region_get_outline(region_struct)
print(outline)
