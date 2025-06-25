from cdb import *
from adapter import *

cdb = CDB()
a = 20
edge1 = [[0,0], [0,a]]
edge2 = [[0,a], [a,a]]
edge3 = [[a,0], [a,a]]
edge4 = []  #[[0,0], [a,0]]
for i in range(0, a+1):
    edge4.append([i, 0])
    
pattern_lines_x = []
pattern_lines_y = [[[3, -10], [3, a+10]], [[4, -10], [4, a+10]]]

cdb.add_pattern_line([edge1])
cdb.add_pattern_line([edge2])
cdb.add_pattern_line([edge3])
cdb.add_pattern_line([edge4])
cdb.add_pattern_line(pattern_lines_x)
cdb.add_pattern_line(pattern_lines_y)
build_block_pattern(cdb, 5, pattern_lines_x, pattern_lines_y, edge1, edge2, edge3, edge4)
cdb.show_graph(f"edge1: {len(edge1)-1}, edge4: {len(edge4)-1}")