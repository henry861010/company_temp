from cdb import *

cdb_obj = CDB()
element_size = 3
x_list = [0, 10, 20, 23]
y_list = [0, 10, 20]
cdb_obj.build_block(element_size, x_list, y_list)
cdb_obj.show_2d_graph()