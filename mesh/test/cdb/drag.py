from cdb import *

cdb_obj = CDB()
element_size = 5
x_list = [0, 10]
y_list = [0, 10]
cdb_obj.build_block(element_size, x_list, y_list)
cdb_obj.drag(5, 10)

cdb_obj.generate_cdb(path = 'cdb.txt')