from test.test_util import *
from mesh2D import *
from adapter import *

mesh2D_obj = Mesh2D()
    
a = 100
element_size = 1
edge1 = [[0,0], [a,0]]
edge2 = [[a,0], [a,a]]
edge3 = [[a,a], [2*a,a]]
edge4 = [[2*a,a], [2*a,0]]
edge5 = [[2*a,0], [3*a,0]]
edge6 = [[3*a,0], [3*a,-a]]
edge7 = [[3*a,-a], [2*a,-a]]
edge8 = [[2*a,-a], [2*a,-2*a]]
edge9 = [[2*a,-2*a], [a,-2*a]]
edge10 = [[a,-2*a], [a,-a]]
edge11 = [[a,-a], [0,-a]]
edge12 = [[0,-a], [0,0]]
outline_list = [edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8, edge9, edge10, edge11, edge12]
for i, outline in enumerate(outline_list):
    new_outline = []
    num = int(abs(outline[-1][0] - outline[0][0]) + abs(outline[-1][1] - outline[0][1]))
    x = (outline[-1][0] - outline[0][0]) / num
    y = (outline[-1][1] - outline[0][1]) / num
    for j in range(0, num+1): 
        new_outline.append([outline[0][0]+x*j, outline[0][1]+y*j])
    outline_list[i] = new_outline



pattern_lines_y = [[[-100, 50], [100, 50]]]
pattern_lines_x = [[[50, -100], [50, 100]]]
pattern_lines = ([edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8, pattern_lines_x, pattern_lines_x])

build_layers(cdb_obj = mesh2D_obj, element_sizes = [3,9,27], pattern_lines_x = pattern_lines_x, pattern_lines_y = pattern_lines_y, outline_list = outline_list)

mesh2D_obj.show_info()
mesh2D_obj.show_2d_graph(title=f"edge1: {len(edge1)-1}, edge4: {len(edge4)-1}", pattern_lines=pattern_lines)